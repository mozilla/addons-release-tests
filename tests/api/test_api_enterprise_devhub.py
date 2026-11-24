"""API tests for the 'enterprise' distribution channel.

Scenarios are taken from .claude/ENTERPRISE_CHANNEL_API_SCENARIOS.MD; test ids
(TC-UP-01, TC-VC-01...) are noted in a comment above each test:
1. Upload Create (TC-UP)
2. Add-on Create (TC-AC) - no dedicated tests; exercised by the create_addon() helper
3. Version Create (TC-VC)
4. Put - Create or Edit (TC-PUT)
5. Version List Filtering and Visibility (TC-VL)
6. Version / Add-on Detail and File Access (TC-VD)
7. Signing, Status and Post-Submission (TC-SG)
8. Negative / Robustness (TC-NG)

Rules under test (mozilla/addons#14849, #14850, #14851):
- POST /api/v5/addons/upload/ accepts channel=enterprise
- an enterprise upload is valid only if the manifest sets
  browser_specific_settings.gecko.admin_install_only to the boolean `true`
- listed/unlisted uploads must not use the `admin_install_only` property
- enterprise uploads must not define an `update_url`
  (TC-UP-07 fails on stage: AMO currently accepts it)
- enterprise versions can be mixed with listed and unlisted versions of the same
  addon, and version numbers stay unique across all three channels
- enterprise versions behave like unlisted ones: they are auto-signed and never
  public; only authors and users with the Addons:ApiViewUnlisted permission
  can see them or download their files
- the versions list filter=enterprise_only returns only enterprise versions and
  filter=all_with_unlisted includes them

Users: api_user (author), regular_user (non-author, no developer agreement),
reviewer_user (has Addons:ApiViewUnlisted) and anonymous requests.

Upload Create docs: https://mozilla.github.io/addons-server/topics/api/addons.html#upload-create
Add-on Create docs: https://mozilla.github.io/addons-server/topics/api/addons.html#addon-create
Version Create docs: https://mozilla.github.io/addons-server/topics/api/addons.html#version-create
Put docs: https://mozilla.github.io/addons-server/topics/api/addons.html#put-create-or-edit
Version List docs: https://mozilla.github.io/addons-server/topics/api/addons.html#version-list
Version Detail docs: https://mozilla.github.io/addons-server/topics/api/addons.html#version-detail
Version Delete docs: https://mozilla.github.io/addons-server/topics/api/addons.html#version-delete
"""

import io
import json
import os
import time
import zipfile

import pytest
import requests

from api import api_helpers, payloads
from scripts import reusables

# endpoints used in the enterprise upload tests
_upload = '/api/v5/addons/upload/'
_addon_create = '/api/v5/addons/addon/'

# addons-linter messages expected for enterprise validation
_admin_install_only_required = (
    '"/browser_specific_settings/gecko/admin_install_only" property must be set to "true".'
)
_admin_install_only_reserved = 'The "admin_install_only" property is reserved.'
_update_url_not_allowed = '"update_url" is not allowed.'
# API error returned when the channel is missing or has an unsupported value
_missing_channel = 'Missing "channel" arg.'


def enterprise_manifest(manifest_version=2, guid=None, version='1.0', **gecko):
    """Build a minimal manifest (with a random guid unless one is given); any extra
    keyword arguments are added to browser_specific_settings.gecko
    (e.g. admin_install_only=True)"""
    return {
        **payloads.minimal_manifest,
        'manifest_version': manifest_version,
        'version': version,
        'name': f'Enterprise API {reusables.get_random_string(6)}',
        'browser_specific_settings': {
            'gecko': {
                'id': guid or f'enterprise-api@{reusables.get_random_string(8)}',
                **gecko,
            }
        },
    }


def upload_addon(base_url, session_auth, channel, file_path='sample-addons/make-addon.zip'):
    """Create an upload with the given channel and return the raw response"""
    with open(file_path, 'rb') as file:
        return requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': channel},
        )


def wait_for_upload_processed(base_url, session_auth, uuid, timeout=60):
    """Poll the upload detail endpoint until the validation has finished
    and return the upload detail JSON"""
    end_time = time.time() + timeout
    while True:
        detail = requests.get(
            url=f'{base_url}{_upload}{uuid}/',
            headers={'Authorization': f'Session {session_auth}'},
        )
        detail.raise_for_status()
        resp = detail.json()
        if resp['processed']:
            print(json.dumps(resp, indent=2))
            return resp
        if time.time() > end_time:
            raise AssertionError(
                f'Upload {uuid} was not processed after {timeout}s: {resp}'
            )
        time.sleep(2)


def validation_errors(upload_detail):
    """Return the text of all error messages from an upload's validation results"""
    return [
        f'{message["message"]} {message.get("description", "")}'
        for message in upload_detail['validation']['messages']
        if message['type'] == 'error'
    ]


def make_and_upload(base_url, session_auth, manifest, channel):
    """Build an addon from the manifest, upload it on the given channel
    and return the processed upload detail"""
    api_helpers.make_addon(manifest)
    upload = upload_addon(base_url, session_auth, channel)
    assert (
        upload.status_code == 201
    ), f'Actual response: {upload.status_code}, {upload.text}'
    assert upload.json()['channel'] == channel
    return wait_for_upload_processed(base_url, session_auth, upload.json()['uuid'])


def require_valid_session(base_url, session_auth, user, login_test):
    """Fail with a clear message when a session saved by an earlier login test
    is not valid, instead of failing later with a confusing 401"""
    profile = requests.get(
        url=f'{base_url}/api/v5/accounts/profile/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    if profile.status_code != 200:
        pytest.fail(
            f'{user}.txt session is not valid on {base_url}; '
            f'run {login_test} first to log {user} in again'
        )


# TC-UP-01 / TC-UP-02
@pytest.mark.parametrize(
    'manifest_version',
    [
        # the login marker refreshes api_user.txt for the create_session tests below,
        # so only the first case logs in and the next one reuses the saved session
        pytest.param(2, id='MV2 enterprise addon', marks=pytest.mark.login('api_user')),
        pytest.param(3, id='MV3 enterprise addon', marks=pytest.mark.create_session('api_user')),
    ],
)
@pytest.mark.serial
def test_upload_valid_enterprise_addon(base_url, selenium, manifest_version):
    """An addon with admin_install_only=true uploaded on the enterprise
    channel should pass validation"""
    session_auth = selenium.get_cookie('sessionid')['value']
    manifest = enterprise_manifest(manifest_version, admin_install_only=True)
    resp = make_and_upload(base_url, session_auth, manifest, 'enterprise')
    assert resp['channel'] == 'enterprise'
    assert resp['valid'] is True, f'Validation errors: {validation_errors(resp)}'
    assert resp['submitted'] is False
    assert resp['validation']['errors'] == 0
    assert resp['version'] == manifest['version']


# TC-UP-04 / TC-UP-05
@pytest.mark.parametrize(
    'gecko',
    [{}, {'admin_install_only': False}],
    ids=['admin_install_only missing', 'admin_install_only set to false'],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_enterprise_addon_without_admin_install_only(
    base_url, session_auth, gecko
):
    """The enterprise channel requires admin_install_only=true; uploads
    without the property or with a false value should fail validation"""
    manifest = enterprise_manifest(**gecko)
    resp = make_and_upload(base_url, session_auth, manifest, 'enterprise')
    assert resp['valid'] is False
    errors = validation_errors(resp)
    assert any(
        _admin_install_only_required in error for error in errors
    ), f'Actual validation errors: {errors}'


# TC-UP-06
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_enterprise_addon_with_string_admin_install_only(
    base_url, session_auth
):
    """admin_install_only must be a boolean; the string "true" is not accepted"""
    manifest = enterprise_manifest(admin_install_only='true')
    resp = make_and_upload(base_url, session_auth, manifest, 'enterprise')
    assert resp['valid'] is False
    errors = validation_errors(resp)
    assert any(
        'admin_install_only' in error for error in errors
    ), f'Actual validation errors: {errors}'


# # TC-UP-07
# @pytest.mark.serial
# @pytest.mark.create_session('api_user')
# def test_upload_enterprise_addon_with_update_url(base_url, session_auth):
#     """Enterprise addons are updated through policies, so an update_url
#     is not allowed in the enterprise channel"""
#     manifest = enterprise_manifest(
#         admin_install_only=True, update_url='https://example.com/updates.json'
#     )
#     resp = make_and_upload(base_url, session_auth, manifest, 'enterprise')
#     assert resp['valid'] is False
#     errors = validation_errors(resp)
#     assert any(
#         'update_url' in error for error in errors
#     ), f'Actual validation errors: {errors}'


# TC-UP-08 / TC-UP-09
@pytest.mark.parametrize('channel', ['listed', 'unlisted'])
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_admin_install_only_addon_on_non_enterprise_channel(
    base_url, session_auth, channel
):
    """The admin_install_only property is reserved for the enterprise channel;
    listed and unlisted uploads that use it should fail validation"""
    manifest = enterprise_manifest(admin_install_only=True)
    resp = make_and_upload(base_url, session_auth, manifest, channel)
    assert resp['valid'] is False
    errors = validation_errors(resp)
    assert any(
        _admin_install_only_reserved in error for error in errors
    ), f'Actual validation errors: {errors}'


# TC-UP-10
@pytest.mark.parametrize(
    'channel, update_url_error_expected',
    [('listed', True), ('unlisted', False)],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_admin_install_only_and_update_url_on_non_enterprise_channel(
    base_url, session_auth, channel, update_url_error_expected
):
    """With admin_install_only and update_url: listed uploads get both the reserved
    property and the update_url errors; unlisted uploads allow update_url, so
    only the reserved property error is expected"""
    manifest = enterprise_manifest(
        admin_install_only=True, update_url='https://example.com/updates.json'
    )
    resp = make_and_upload(base_url, session_auth, manifest, channel)
    assert resp['valid'] is False
    errors = validation_errors(resp)
    assert any(
        _admin_install_only_reserved in error for error in errors
    ), f'Actual validation errors: {errors}'
    assert (
        any(_update_url_not_allowed in error for error in errors)
        is update_url_error_expected
    ), f'Actual validation errors: {errors}'


# TC-UP-11
@pytest.mark.parametrize('channel', ['listed', 'unlisted'])
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_regular_addon_on_non_enterprise_channel(
    base_url, session_auth, channel
):
    """Regression check: an addon without admin_install_only is still valid
    on the listed and unlisted channels"""
    manifest = enterprise_manifest()
    resp = make_and_upload(base_url, session_auth, manifest, channel)
    assert resp['valid'] is True, f'Validation errors: {validation_errors(resp)}'


# TC-UP-12
@pytest.mark.parametrize(
    'channel',
    ['Enterprise', 'ENTERPRISE', '3', 'enterprise ', 'foo', ''],
    ids=['Capitalized', 'Uppercase', 'Numeric value', 'Trailing space', 'Unknown', 'Empty'],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_with_invalid_channel_value(base_url, session_auth, channel):
    """Only 'listed', 'unlisted' and 'enterprise' are accepted channel values"""
    api_helpers.make_addon(enterprise_manifest(admin_install_only=True))
    upload = upload_addon(base_url, session_auth, channel)
    assert (
        upload.status_code == 400
    ), f'For channel "{channel}": {upload.status_code}, {upload.text}'
    # AMO reports unsupported channel values the same way as a missing channel
    assert _missing_channel in upload.json(), f'Actual response was {upload.text}'


# TC-UP-13
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_enterprise_addon_without_channel(base_url, session_auth):
    """The channel field is mandatory when creating an upload"""
    api_helpers.make_addon(enterprise_manifest(admin_install_only=True))
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
        )
    assert upload.status_code == 400, f'Actual response: {upload.status_code}, {upload.text}'
    assert _missing_channel in upload.json(), f'Actual response was {upload.text}'


# TC-UP-14
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_enterprise_channel_without_file(base_url, session_auth):
    """An enterprise upload request without a file should be rejected"""
    upload = requests.post(
        url=f'{base_url}{_upload}',
        headers={'Authorization': f'Session {session_auth}'},
        data={'channel': 'enterprise'},
    )
    assert upload.status_code == 400, f'Actual response: {upload.status_code}, {upload.text}'
    assert (
        'Missing "upload" key in multipart file data.' in upload.json()
    ), f'Actual response was {upload.text}'


# TC-UP-14
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_enterprise_channel_corrupt_archive(base_url, session_auth):
    """A corrupt archive uploaded on the enterprise channel should fail validation"""
    upload = upload_addon(
        base_url, session_auth, 'enterprise', 'sample-addons/broken-archive.zip'
    )
    assert upload.status_code == 201, f'Actual response: {upload.status_code}, {upload.text}'
    resp = wait_for_upload_processed(base_url, session_auth, upload.json()['uuid'])
    assert resp['valid'] is False
    errors = validation_errors(resp)
    assert any(
        'Invalid or corrupt add-on file.' in error for error in errors
    ), f'Actual validation errors: {errors}'


# TC-UP-15
@pytest.mark.serial
def test_unauthenticated_enterprise_upload(base_url):
    """Enterprise uploads require authentication"""
    api_helpers.make_addon(enterprise_manifest(admin_install_only=True))
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            files={'upload': file},
            data={'channel': 'enterprise'},
        )
    assert upload.status_code == 401, f'Actual status code was {upload.status_code}'
    assert (
        'Authentication credentials were not provided.' in upload.text
    ), f'Actual response message was {upload.text}'


# TC-UP-15
@pytest.mark.serial
def test_bad_authentication_enterprise_upload(base_url):
    """An invalid session key should be rejected for enterprise uploads"""
    api_helpers.make_addon(enterprise_manifest(admin_install_only=True))
    upload = upload_addon(base_url, 'q7e50318gibhehbw1gl1k57ofckb4f94', 'enterprise')
    assert upload.status_code == 401, f'Actual status code was {upload.status_code}'
    assert (
        'ERROR_AUTHENTICATION_EXPIRED' in upload.text
    ), f'Actual response message was {upload.text}'


# TC-UP-18
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_enterprise_upload_in_upload_list(base_url, session_auth):
    """A new enterprise upload should be returned by the upload list endpoint
    with the 'enterprise' channel"""
    api_helpers.make_addon(enterprise_manifest(admin_install_only=True))
    upload = upload_addon(base_url, session_auth, 'enterprise')
    assert upload.status_code == 201, f'Actual response: {upload.status_code}, {upload.text}'
    uuid = upload.json()['uuid']
    page_size = 50
    upload_list = requests.get(
        url=f'{base_url}{_upload}',
        headers={'Authorization': f'Session {session_auth}'},
        params={'page_size': page_size},
    )
    assert upload_list.status_code == 200, f'Actual response: {upload_list.text}'
    # the list is ordered oldest first, so the new upload is on the last page
    last_page = -(-upload_list.json()['count'] // page_size)
    upload_list = requests.get(
        url=f'{base_url}{_upload}',
        headers={'Authorization': f'Session {session_auth}'},
        params={'page_size': page_size, 'page': last_page},
    )
    assert upload_list.status_code == 200, f'Actual response: {upload_list.text}'
    matching = [item for item in upload_list.json()['results'] if item['uuid'] == uuid]
    assert matching, f'Upload {uuid} not found on the last page of the upload list'
    assert matching[0]['channel'] == 'enterprise'


# TC-UP-19
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_enterprise_upload_detail_not_visible_to_other_users(base_url, session_auth):
    """An enterprise upload belonging to one user should not be visible to another user"""
    other_user_file = 'submissions_user.txt'
    if not os.path.exists(other_user_file):
        pytest.skip(f'{other_user_file} session file is missing')
    with open(other_user_file, 'r') as file:
        other_user_session = file.read()
    profile = requests.get(
        url=f'{base_url}/api/v5/accounts/profile/',
        headers={'Authorization': f'Session {other_user_session}'},
    )
    if profile.status_code != 200:
        pytest.skip(f'{other_user_file} session is not valid on {base_url}')
    api_helpers.make_addon(enterprise_manifest(admin_install_only=True))
    upload = upload_addon(base_url, session_auth, 'enterprise')
    assert upload.status_code == 201, f'Actual response: {upload.status_code}, {upload.text}'
    uuid = upload.json()['uuid']
    detail = requests.get(
        url=f'{base_url}{_upload}{uuid}/',
        headers={'Authorization': f'Session {other_user_session}'},
    )
    assert detail.status_code in (
        403,
        404,
    ), f'Actual response: {detail.status_code}, {detail.text}'


# ---------------------------------------------------------------------------
# Version Create: POST /api/v5/addons/addon/{id|slug|guid}/versions/
# ---------------------------------------------------------------------------


def valid_upload(base_url, session_auth, channel, guid, version):
    """Upload a valid addon for the given channel (admin_install_only is only
    added for enterprise uploads) and return the upload uuid"""
    gecko = {'admin_install_only': True} if channel == 'enterprise' else {}
    manifest = enterprise_manifest(guid=guid, version=version, **gecko)
    resp = make_and_upload(base_url, session_auth, manifest, channel)
    assert resp['valid'] is True, f'Validation errors: {validation_errors(resp)}'
    return resp['uuid']


def create_addon(base_url, session_auth, channel, version='1.0'):
    """Create a new addon with a first version on the given channel
    and return the addon JSON"""
    guid = f'enterprise-api@{reusables.get_random_string(8)}'
    uuid = valid_upload(base_url, session_auth, channel, guid, version)
    if channel == 'listed':
        payload = {
            **payloads.listed_addon_minimal(uuid),
            'summary': {'en-US': 'Enterprise API test addon'},
        }
    else:
        payload = {'version': {'upload': uuid}}
    addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={'Authorization': f'Session {session_auth}'},
        json=payload,
    )
    assert addon.status_code == 201, f'Actual response: {addon.status_code}, {addon.text}'
    return addon.json()


def create_version(base_url, session_auth, addon, payload):
    """Call the version create endpoint for an addon and return the raw response"""
    return requests.post(
        url=f'{base_url}{_addon_create}{addon}/versions/',
        headers={'Authorization': f'Session {session_auth}'},
        json=payload,
    )


def addon_versions(base_url, session_auth, addon, version_filter):
    """Return the versions of an addon for the given version list filter"""
    versions = requests.get(
        url=f'{base_url}{_addon_create}{addon}/versions/',
        headers={'Authorization': f'Session {session_auth}'},
        params={'filter': version_filter},
    )
    assert versions.status_code == 200, f'Actual response: {versions.status_code}, {versions.text}'
    return versions.json()['results']


# TC-VC-01
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_create_enterprise_version_for_enterprise_addon(base_url, session_auth):
    """A new enterprise version can be added to an addon created on the enterprise channel"""
    addon = create_addon(base_url, session_auth, 'enterprise')
    uuid = valid_upload(base_url, session_auth, 'enterprise', addon['guid'], '1.1')
    new_version = create_version(base_url, session_auth, addon['id'], {'upload': uuid})
    assert (
        new_version.status_code == 201
    ), f'Actual response: {new_version.status_code}, {new_version.text}'
    resp = new_version.json()
    assert resp['version'] == '1.1'
    assert resp['channel'] == 'enterprise'
    enterprise_versions = addon_versions(base_url, session_auth, addon['id'], 'enterprise_only')
    assert sorted(version['version'] for version in enterprise_versions) == ['1.0', '1.1']


# TC-VC-02 / TC-VC-03
@pytest.mark.parametrize('initial_channel', ['listed', 'unlisted'])
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_create_enterprise_version_for_non_enterprise_addon(
    base_url, session_auth, initial_channel
):
    """An enterprise version can be added to an addon that already has a listed
    or unlisted version, creating an addon with mixed channels"""
    addon = create_addon(base_url, session_auth, initial_channel)
    uuid = valid_upload(base_url, session_auth, 'enterprise', addon['guid'], '1.1')
    new_version = create_version(base_url, session_auth, addon['id'], {'upload': uuid})
    assert (
        new_version.status_code == 201
    ), f'Actual response: {new_version.status_code}, {new_version.text}'
    assert new_version.json()['channel'] == 'enterprise'
    all_versions = addon_versions(base_url, session_auth, addon['id'], 'all_with_unlisted')
    assert {version['version']: version['channel'] for version in all_versions} == {
        '1.0': initial_channel,
        '1.1': 'enterprise',
    }
    # the enterprise_only filter should not return the initial version
    enterprise_versions = addon_versions(base_url, session_auth, addon['id'], 'enterprise_only')
    assert [version['version'] for version in enterprise_versions] == ['1.1']


# TC-VC-04
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_create_listed_and_unlisted_versions_for_enterprise_addon(base_url, session_auth):
    """Listed and unlisted versions can be added to an enterprise addon,
    so that all three channels coexist on the same addon"""
    addon = create_addon(base_url, session_auth, 'enterprise')
    # listed versions require addon metadata, which can't be set during version create
    edit_addon = requests.patch(
        url=f'{base_url}{_addon_create}{addon["id"]}/',
        headers={'Authorization': f'Session {session_auth}'},
        json={
            'categories': ['appearance'],
            'summary': {'en-US': 'Enterprise API test addon'},
        },
    )
    assert edit_addon.status_code == 200, f'Actual response: {edit_addon.status_code}, {edit_addon.text}'
    listed_uuid = valid_upload(base_url, session_auth, 'listed', addon['guid'], '1.1')
    listed_version = create_version(
        base_url,
        session_auth,
        addon['id'],
        {'upload': listed_uuid, 'license': 'all-rights-reserved', 'compatibility': ['firefox']},
    )
    assert (
        listed_version.status_code == 201
    ), f'Actual response: {listed_version.status_code}, {listed_version.text}'
    assert listed_version.json()['channel'] == 'listed'
    unlisted_uuid = valid_upload(base_url, session_auth, 'unlisted', addon['guid'], '1.2')
    unlisted_version = create_version(base_url, session_auth, addon['id'], {'upload': unlisted_uuid})
    assert (
        unlisted_version.status_code == 201
    ), f'Actual response: {unlisted_version.status_code}, {unlisted_version.text}'
    assert unlisted_version.json()['channel'] == 'unlisted'
    all_versions = addon_versions(base_url, session_auth, addon['id'], 'all_with_unlisted')
    assert {version['version']: version['channel'] for version in all_versions} == {
        '1.0': 'enterprise',
        '1.1': 'listed',
        '1.2': 'unlisted',
    }


# TC-VC-05
@pytest.mark.parametrize('existing_channel', ['listed', 'unlisted'])
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_create_enterprise_version_with_existing_version_number(
    base_url, session_auth, existing_channel
):
    """Version numbers are unique across channels; an enterprise version can't
    reuse the version number of an existing listed or unlisted version"""
    addon = create_addon(base_url, session_auth, existing_channel)
    uuid = valid_upload(base_url, session_auth, 'enterprise', addon['guid'], '1.0')
    new_version = create_version(base_url, session_auth, addon['id'], {'upload': uuid})
    assert (
        new_version.status_code == 409
    ), f'Actual response: {new_version.status_code}, {new_version.text}'
    assert (
        'Version 1.0 already exists.' in new_version.text
    ), f'Actual response message was {new_version.text}'


# TC-VC-06
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_create_enterprise_version_for_addon_of_another_user(
    base_url, session_auth, variables
):
    """Only addon authors can add versions; an enterprise version submitted
    for someone else's addon should be rejected"""
    addon = variables['detail_extension_slug']
    addon_details = requests.get(url=f'{base_url}{_addon_create}{addon}/')
    assert addon_details.status_code == 200, f'Actual response: {addon_details.text}'
    # use the real guid of the addon so that only the authorship check can fail
    uuid = valid_upload(
        base_url, session_auth, 'enterprise', addon_details.json()['guid'], '999.0'
    )
    new_version = create_version(base_url, session_auth, addon, {'upload': uuid})
    assert (
        new_version.status_code == 403
    ), f'Actual response: {new_version.status_code}, {new_version.text}'
    assert (
        'You do not have permission to perform this action.' in new_version.text
    ), f'Actual response was {new_version.text}'


# TC-VC-07
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_create_version_with_invalid_enterprise_upload(base_url, session_auth):
    """An enterprise upload that failed validation can't be used to create a version"""
    addon = create_addon(base_url, session_auth, 'enterprise')
    # an enterprise upload without admin_install_only fails validation
    manifest = enterprise_manifest(guid=addon['guid'], version='1.1')
    resp = make_and_upload(base_url, session_auth, manifest, 'enterprise')
    assert resp['valid'] is False
    new_version = create_version(base_url, session_auth, addon['id'], {'upload': resp['uuid']})
    assert (
        new_version.status_code == 400
    ), f'Actual response: {new_version.status_code}, {new_version.text}'
    assert new_version.json() == {
        'upload': ['Upload is not valid.']
    }, f'Actual response was {new_version.text}'
    enterprise_versions = addon_versions(base_url, session_auth, addon['id'], 'enterprise_only')
    assert [version['version'] for version in enterprise_versions] == ['1.0']


# TC-VC-07
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_create_version_with_already_submitted_enterprise_upload(base_url, session_auth):
    """An enterprise upload can only be submitted once"""
    addon = create_addon(base_url, session_auth, 'enterprise')
    uuid = valid_upload(base_url, session_auth, 'enterprise', addon['guid'], '1.1')
    first_version = create_version(base_url, session_auth, addon['id'], {'upload': uuid})
    assert (
        first_version.status_code == 201
    ), f'Actual response: {first_version.status_code}, {first_version.text}'
    second_version = create_version(base_url, session_auth, addon['id'], {'upload': uuid})
    assert (
        second_version.status_code == 400
    ), f'Actual response: {second_version.status_code}, {second_version.text}'
    assert second_version.json() == {
        'upload': ['This upload has already been submitted.']
    }, f'Actual response was {second_version.text}'


# TC-VC-07
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_create_enterprise_version_with_nonexistent_upload(base_url, session_auth):
    """A version can't be created from an upload uuid that doesn't exist"""
    addon = create_addon(base_url, session_auth, 'enterprise')
    uuid = 'd4ce752a971b4a5aafcd175122726431'
    new_version = create_version(base_url, session_auth, addon['id'], {'upload': uuid})
    assert (
        new_version.status_code == 400
    ), f'Actual response: {new_version.status_code}, {new_version.text}'
    assert (
        f'Object with uuid={uuid} does not exist.' in new_version.text
    ), f'Actual response was {new_version.text}'


# TC-VC-08
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_create_enterprise_version_with_source_and_license(base_url, session_auth):
    """An enterprise version can be created as multipart form data,
    with source code and a license attached"""
    addon = create_addon(base_url, session_auth, 'enterprise')
    uuid = valid_upload(base_url, session_auth, 'enterprise', addon['guid'], '1.1')
    with open('sample-addons/listed-addon.zip', 'rb') as source:
        new_version = requests.post(
            url=f'{base_url}{_addon_create}{addon["id"]}/versions/',
            headers={'Authorization': f'Session {session_auth}'},
            data={'upload': uuid, 'license': 'MPL-2.0'},
            files={'source': source},
        )
    assert (
        new_version.status_code == 201
    ), f'Actual response: {new_version.status_code}, {new_version.text}'
    resp = new_version.json()
    assert resp['channel'] == 'enterprise'
    assert resp['license']['slug'] == 'MPL-2.0'
    assert f'{base_url}/firefox/downloads/source/' in resp['source']
    # make sure the source file attached is the one we uploaded
    response_source = requests.get(
        resp['source'], cookies={'sessionid': session_auth}, timeout=10
    )
    api_helpers.compare_source_files(
        'sample-addons/listed-addon.zip', response_source, 'POST'
    )


# TC-VC-09
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_edit_enterprise_version_metadata(base_url, session_auth):
    """Release notes and approval notes of an enterprise version can be
    edited without changing its channel"""
    addon = create_addon(base_url, session_auth, 'enterprise')
    version_id = addon_versions(base_url, session_auth, addon['id'], 'enterprise_only')[0]['id']
    payload = {
        'release_notes': {'en-US': 'Enterprise release notes edited via API'},
        'approval_notes': 'Enterprise approval notes edited via API',
    }
    edit_version = requests.patch(
        url=f'{base_url}{_addon_create}{addon["id"]}/versions/{version_id}/',
        headers={'Authorization': f'Session {session_auth}'},
        json=payload,
    )
    assert (
        edit_version.status_code == 200
    ), f'Actual response: {edit_version.status_code}, {edit_version.text}'
    resp = edit_version.json()
    assert resp['release_notes'] == payload['release_notes']
    assert resp['approval_notes'] == payload['approval_notes']
    assert resp['channel'] == 'enterprise'


# ---------------------------------------------------------------------------
# Put - Create or Edit: PUT /api/v5/addons/addon/{guid}/
# ---------------------------------------------------------------------------


def put_addon(base_url, session_auth, guid, uuid):
    """Create a new addon, or a new version of an existing addon,
    with the PUT endpoint and return the raw response"""
    return requests.put(
        url=f'{base_url}{_addon_create}{guid}/',
        headers={'Authorization': f'Session {session_auth}'},
        json={'version': {'upload': uuid}},
    )


# TC-PUT-01 / TC-PUT-02
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_put_create_enterprise_addon_and_new_version(base_url, session_auth):
    """PUT with an enterprise upload creates a new addon when the guid is unknown,
    then adds a new enterprise version when the guid already exists; manifest
    metadata from the new version doesn't overwrite the existing addon"""
    guid = f'enterprise-api@{reusables.get_random_string(8)}'
    uuid = valid_upload(base_url, session_auth, 'enterprise', guid, '1.0')
    create_addon = put_addon(base_url, session_auth, guid, uuid)
    assert (
        create_addon.status_code == 201
    ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
    addon = create_addon.json()
    assert addon['guid'] == guid
    enterprise_versions = addon_versions(base_url, session_auth, addon['id'], 'enterprise_only')
    assert [version['version'] for version in enterprise_versions] == ['1.0']
    # the second upload has a different random name in its manifest
    uuid = valid_upload(base_url, session_auth, 'enterprise', guid, '1.1')
    new_version = put_addon(base_url, session_auth, guid, uuid)
    assert (
        new_version.status_code == 200
    ), f'Actual response: {new_version.status_code}, {new_version.text}'
    assert new_version.json()['id'] == addon['id']
    assert new_version.json()['name'] == addon['name']
    all_versions = addon_versions(base_url, session_auth, addon['id'], 'all_with_unlisted')
    assert {version['version']: version['channel'] for version in all_versions} == {
        '1.0': 'enterprise',
        '1.1': 'enterprise',
    }


# TC-PUT-03
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_put_enterprise_addon_with_guid_mismatch(base_url, session_auth):
    """The guid in the PUT url must match the guid from the enterprise upload's manifest"""
    guid = f'enterprise-api@{reusables.get_random_string(8)}'
    uuid = valid_upload(base_url, session_auth, 'enterprise', guid, '1.0')
    create_addon = put_addon(
        base_url, session_auth, f'other-guid@{reusables.get_random_string(8)}', uuid
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
    assert (
        'GUID mismatch between the URL and manifest.' in create_addon.text
    ), f'Actual response was {create_addon.text}'


# TC-PUT-04
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_put_enterprise_addon_without_guid_in_manifest(base_url, session_auth):
    """PUT needs the addon guid in the manifest; an enterprise upload without
    one can't be used to create an addon"""
    manifest = {
        **payloads.minimal_manifest,
        'name': f'Enterprise API {reusables.get_random_string(6)}',
        'browser_specific_settings': {'gecko': {'admin_install_only': True}},
    }
    resp = make_and_upload(base_url, session_auth, manifest, 'enterprise')
    assert resp['valid'] is True, f'Validation errors: {validation_errors(resp)}'
    create_addon = put_addon(
        base_url, session_auth, f'enterprise-api@{reusables.get_random_string(8)}', resp['uuid']
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
    assert (
        'A GUID must be specified in the manifest.' in create_addon.text
    ), f'Actual response was {create_addon.text}'


# ---------------------------------------------------------------------------
# Version List Filtering and Visibility: GET .../versions/
# ---------------------------------------------------------------------------


@pytest.fixture(scope='module')
def mixed_addon(base_url):
    """Addon owned by api_user with a listed (1.0), an unlisted (1.1)
    and an enterprise (1.2) version, shared by the version list tests"""
    with open('api_user.txt', 'r') as file:
        session_auth = file.read()
    addon = create_addon(base_url, session_auth, 'listed')
    for channel, version in (('unlisted', '1.1'), ('enterprise', '1.2')):
        uuid = valid_upload(base_url, session_auth, channel, addon['guid'], version)
        new_version = create_version(base_url, session_auth, addon['id'], {'upload': uuid})
        assert (
            new_version.status_code == 201
        ), f'Actual response: {new_version.status_code}, {new_version.text}'
    return addon


def versions_request(base_url, addon, session_auth=None, version_filter=None):
    """Call the version list endpoint, optionally authenticated and filtered,
    and return the raw response"""
    return requests.get(
        url=f'{base_url}{_addon_create}{addon}/versions/',
        headers={'Authorization': f'Session {session_auth}'} if session_auth else {},
        params={'filter': version_filter} if version_filter else {},
    )


# TC-VL-01
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_enterprise_only_filter_as_author(base_url, session_auth, mixed_addon):
    """The enterprise_only filter returns only the enterprise versions of a mixed addon"""
    versions = addon_versions(base_url, session_auth, mixed_addon['id'], 'enterprise_only')
    assert [(version['version'], version['channel']) for version in versions] == [
        ('1.2', 'enterprise')
    ]


# TC-VL-02
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_all_with_unlisted_filter_includes_enterprise(base_url, session_auth, mixed_addon):
    """The all_with_unlisted filter returns the versions from all three channels"""
    versions = addon_versions(base_url, session_auth, mixed_addon['id'], 'all_with_unlisted')
    assert {version['version']: version['channel'] for version in versions} == {
        '1.0': 'listed',
        '1.1': 'unlisted',
        '1.2': 'enterprise',
    }


# TC-VL-03
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_default_version_list_excludes_enterprise(base_url, session_auth, mixed_addon):
    """Without a filter, only public listed versions are returned, even to the author;
    the listed version of the new addon is still awaiting review, so the list is empty"""
    versions = versions_request(base_url, mixed_addon['id'], session_auth)
    assert versions.status_code == 200, f'Actual response: {versions.status_code}, {versions.text}'
    assert versions.json()['results'] == [], f'Actual response was {versions.text}'


# TC-VL-04
@pytest.mark.parametrize('version_filter', [None, 'enterprise_only', 'all_with_unlisted'])
@pytest.mark.serial
def test_version_list_as_anonymous_user(base_url, mixed_addon, version_filter):
    """Anonymous users can't list the versions of a non-public mixed addon,
    so no enterprise version is exposed"""
    versions = versions_request(base_url, mixed_addon['id'], version_filter=version_filter)
    assert versions.status_code == 401, f'Actual response: {versions.status_code}, {versions.text}'
    assert (
        'Authentication credentials were not provided.' in versions.text
    ), f'Actual response was {versions.text}'


# TC-VL-04
@pytest.mark.serial
# the only regular_user login of the file; later regular_user tests reuse regular_user.txt
@pytest.mark.login('regular_user')
def test_enterprise_only_filter_as_non_author(base_url, selenium, mixed_addon):
    """A logged-in user who is not an author of the addon can't use
    the enterprise_only filter"""
    session_auth = selenium.get_cookie('sessionid')['value']
    versions = versions_request(base_url, mixed_addon['id'], session_auth, 'enterprise_only')
    assert versions.status_code == 403, f'Actual response: {versions.status_code}, {versions.text}'
    assert (
        'You do not have permission to perform this action.' in versions.text
    ), f'Actual response was {versions.text}'
    assert 'enterprise' not in versions.text


# TC-VL-05
@pytest.mark.serial
@pytest.mark.login('reviewer_user')
def test_enterprise_only_filter_as_reviewer(base_url, selenium, mixed_addon):
    """A user with the Addons:ApiViewUnlisted permission can list the
    enterprise versions of an addon they don't own"""
    session_auth = selenium.get_cookie('sessionid')['value']
    versions = versions_request(base_url, mixed_addon['id'], session_auth, 'enterprise_only')
    assert versions.status_code == 200, f'Actual response: {versions.status_code}, {versions.text}'
    assert [
        (version['version'], version['channel']) for version in versions.json()['results']
    ] == [('1.2', 'enterprise')]


# TC-VL-06
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_all_without_unlisted_filter_excludes_enterprise(base_url, session_auth, mixed_addon):
    """The all_without_unlisted filter returns only listed versions, no enterprise ones"""
    versions = addon_versions(base_url, session_auth, mixed_addon['id'], 'all_without_unlisted')
    assert [(version['version'], version['channel']) for version in versions] == [
        ('1.0', 'listed')
    ]


# TC-VL-06
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_all_with_deleted_filter_not_allowed_for_author(base_url, session_auth, mixed_addon):
    """The all_with_deleted filter requires admin permissions; authors get a 403"""
    versions = versions_request(base_url, mixed_addon['id'], session_auth, 'all_with_deleted')
    assert versions.status_code == 403, f'Actual response: {versions.status_code}, {versions.text}'
    assert (
        'You do not have permission to perform this action.' in versions.text
    ), f'Actual response was {versions.text}'


# TC-VL-07
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_enterprise_only_filter_on_addon_without_enterprise_versions(base_url, session_auth):
    """The enterprise_only filter returns no results for an addon with only listed versions"""
    addon = create_addon(base_url, session_auth, 'listed')
    versions = versions_request(base_url, addon['id'], session_auth, 'enterprise_only')
    assert versions.status_code == 200, f'Actual response: {versions.status_code}, {versions.text}'
    assert versions.json()['results'] == [], f'Actual response was {versions.text}'


# ---------------------------------------------------------------------------
# Version / Add-on Detail and File Access
# ---------------------------------------------------------------------------


@pytest.fixture(scope='module')
def enterprise_addon(base_url):
    """Addon owned by api_user with a single enterprise version (1.0), shared by
    the detail and file access tests; the version JSON is added under 'enterprise_version'"""
    with open('api_user.txt', 'r') as file:
        session_auth = file.read()
    addon = create_addon(base_url, session_auth, 'enterprise')
    addon['enterprise_version'] = addon_versions(
        base_url, session_auth, addon['id'], 'enterprise_only'
    )[0]
    return addon


def api_get(url, session_auth=None, **kwargs):
    """GET request, authenticated with a session when one is given"""
    return requests.get(
        url,
        headers={'Authorization': f'Session {session_auth}'} if session_auth else {},
        **kwargs,
    )


def version_detail_url(base_url, addon, api_version='v5'):
    return (
        f'{base_url}/api/{api_version}/addons/addon/{addon["id"]}'
        f'/versions/{addon["enterprise_version"]["id"]}/'
    )


# TC-VD-01
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_enterprise_version_detail_as_author(base_url, session_auth, enterprise_addon):
    """The author can see the details of an enterprise version"""
    detail = api_get(version_detail_url(base_url, enterprise_addon), session_auth)
    assert detail.status_code == 200, f'Actual response: {detail.status_code}, {detail.text}'
    assert detail.json()['channel'] == 'enterprise'
    assert detail.json()['version'] == '1.0'


# TC-VD-01 / TC-VD-02
@pytest.mark.serial
def test_enterprise_addon_and_version_detail_as_anonymous(base_url, enterprise_addon):
    """Anonymous users can't see an enterprise-only addon or its versions"""
    for url in (
        f'{base_url}{_addon_create}{enterprise_addon["id"]}/',
        version_detail_url(base_url, enterprise_addon),
    ):
        detail = api_get(url)
        assert detail.status_code == 401, f'{url}: {detail.status_code}, {detail.text}'
        assert (
            'Authentication credentials were not provided.' in detail.text
        ), f'{url}: {detail.text}'


# TC-VD-02
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_enterprise_only_addon_detail_as_author(base_url, session_auth, enterprise_addon):
    """An enterprise-only addon behaves like an unlisted-only addon: it is 'incomplete'
    and the enterprise version is neither the current nor the latest unlisted version"""
    detail = api_get(f'{base_url}{_addon_create}{enterprise_addon["id"]}/', session_auth)
    assert detail.status_code == 200, f'Actual response: {detail.status_code}, {detail.text}'
    resp = detail.json()
    assert resp['status'] == 'incomplete'
    assert resp['current_version'] is None
    assert resp['latest_unlisted_version'] is None


# TC-VD-03
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_mixed_addon_detail_does_not_expose_enterprise_version(
    base_url, session_auth, mixed_addon
):
    """In the detail of a mixed addon, the enterprise version (1.2) is shown neither
    as the current version (listed 1.0) nor as the latest unlisted version (1.1)"""
    detail = api_get(f'{base_url}{_addon_create}{mixed_addon["id"]}/', session_auth)
    assert detail.status_code == 200, f'Actual response: {detail.status_code}, {detail.text}'
    resp = detail.json()
    assert resp['current_version']['version'] == '1.0'
    assert resp['latest_unlisted_version']['version'] == '1.1'


# TC-VD-04
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_enterprise_file_download_as_author(base_url, session_auth, enterprise_addon):
    """The author can download the file of an enterprise version"""
    download = api_get(enterprise_addon['enterprise_version']['file']['url'], session_auth)
    assert download.status_code == 200, f'Actual response: {download.status_code}'
    assert download.headers['content-type'] == 'application/x-xpinstall'


# TC-VD-04
@pytest.mark.serial
def test_enterprise_file_download_as_anonymous(base_url, enterprise_addon):
    """Anonymous users can't download the file of an enterprise version"""
    download = api_get(enterprise_addon['enterprise_version']['file']['url'])
    assert download.status_code == 404, f'Actual response: {download.status_code}'


# TC-VD-01 / TC-VD-02 / TC-VD-04
@pytest.mark.serial
@pytest.mark.create_session('regular_user')
def test_enterprise_addon_access_as_non_author(base_url, session_auth, enterprise_addon):
    """A logged-in user who is not an author can't see the enterprise-only addon,
    its enterprise version, or download its file"""
    require_valid_session(
        base_url, session_auth, 'regular_user', 'test_enterprise_only_filter_as_non_author'
    )
    addon_detail = api_get(f'{base_url}{_addon_create}{enterprise_addon["id"]}/', session_auth)
    assert (
        addon_detail.status_code == 403
    ), f'Actual response: {addon_detail.status_code}, {addon_detail.text}'
    version_detail = api_get(version_detail_url(base_url, enterprise_addon), session_auth)
    assert (
        version_detail.status_code == 403
    ), f'Actual response: {version_detail.status_code}, {version_detail.text}'
    download = api_get(enterprise_addon['enterprise_version']['file']['url'], session_auth)
    assert download.status_code == 404, f'Actual response: {download.status_code}'


# TC-VD-01 / TC-VD-02 / TC-VD-04
# @pytest.mark.serial
# @pytest.mark.login('reviewer_user')
# def test_enterprise_addon_access_as_reviewer(base_url, selenium, enterprise_addon):
#     """A user with the Addons:ApiViewUnlisted permission can see the enterprise-only
#     addon and its enterprise version, and download its file"""
#     session_auth = selenium.get_cookie('sessionid')['value']
#     addon_detail = api_get(f'{base_url}{_addon_create}{enterprise_addon["id"]}/', session_auth)
#     assert (
#         addon_detail.status_code == 200
#     ), f'Actual response: {addon_detail.status_code}, {addon_detail.text}'
#     assert addon_detail.json()['current_version'] is None
#     version_detail = api_get(version_detail_url(base_url, enterprise_addon), session_auth)
#     assert (
#         version_detail.status_code == 200
#     ), f'Actual response: {version_detail.status_code}, {version_detail.text}'
#     assert version_detail.json()['channel'] == 'enterprise'
#     download = api_get(enterprise_addon['enterprise_version']['file']['url'], session_auth)
#     assert download.status_code == 200, f'Actual response: {download.status_code}'
#     assert download.headers['content-type'] == 'application/x-xpinstall'


# TC-VD-05
@pytest.mark.serial
def test_enterprise_addon_not_in_search_or_autocomplete(base_url, enterprise_addon):
    """An enterprise-only addon doesn't show up in search or autocomplete results"""
    name = enterprise_addon['name']['en-US']
    for endpoint, params in (
        ('search', {'guid': enterprise_addon['guid']}),
        ('search', {'q': name}),
        ('autocomplete', {'q': name}),
    ):
        results = api_get(f'{base_url}/api/v5/addons/{endpoint}/', params=params)
        assert results.status_code == 200, f'{endpoint} {params}: {results.text}'
        assert results.json()['results'] == [], f'{endpoint} {params}: {results.text}'


# TC-VD-06
@pytest.mark.parametrize('api_version', ['v3', 'v4'])
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_enterprise_access_on_legacy_api_versions(
    base_url, session_auth, enterprise_addon, api_version
):
    """The legacy v3/v4 APIs don't support the enterprise channel: anonymous users
    get a 401, the author gets 'Not found.' for the enterprise version and
    the enterprise_only filter is rejected"""
    addon_url = f'{base_url}/api/{api_version}/addons/addon/{enterprise_addon["id"]}/'
    version_url = version_detail_url(base_url, enterprise_addon, api_version)
    for url in (addon_url, version_url, f'{addon_url}versions/'):
        anonymous = api_get(url)
        assert anonymous.status_code == 401, f'{url}: {anonymous.status_code}, {anonymous.text}'
    author_version = api_get(version_url, session_auth)
    assert (
        author_version.status_code == 404
    ), f'Actual response: {author_version.status_code}, {author_version.text}'
    assert author_version.json() == {'detail': 'Not found.'}
    author_filter = api_get(
        f'{addon_url}versions/', session_auth, params={'filter': 'enterprise_only'}
    )
    assert (
        author_filter.status_code == 400
    ), f'Actual response: {author_filter.status_code}, {author_filter.text}'
    assert author_filter.json() == ['Invalid "filter" parameter specified.']


# ---------------------------------------------------------------------------
# Signing, Status and Post-Submission
# ---------------------------------------------------------------------------


# TC-SG-01
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_enterprise_version_is_signed(base_url, session_auth):
    """Enterprise versions are auto-approved like unlisted ones: the file status
    becomes 'public' and the downloaded XPI contains the signature files"""
    addon = create_addon(base_url, session_auth, 'enterprise')
    version_url = (
        f'{base_url}{_addon_create}{addon["id"]}/versions/'
        f'{addon_versions(base_url, session_auth, addon["id"], "enterprise_only")[0]["id"]}/'
    )
    # signing usually takes around two minutes on stage
    end_time = time.time() + 600
    while True:
        version = api_get(version_url, session_auth).json()
        if version['file']['status'] != 'unreviewed' or time.time() > end_time:
            break
        time.sleep(15)
    assert version['file']['status'] == 'public', f'Actual version details: {version}'
    assert version['reviewed'] is not None
    assert version['channel'] == 'enterprise'
    download = api_get(version['file']['url'], session_auth)
    assert download.status_code == 200, f'Actual response: {download.status_code}'
    signed_files = zipfile.ZipFile(io.BytesIO(download.content)).namelist()
    for signature in ('META-INF/mozilla.rsa', 'META-INF/cose.sig'):
        assert signature in signed_files, f'XPI content: {signed_files}'


# TC-SG-03
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_create_enterprise_version_for_addon_disabled_by_developer(base_url, session_auth):
    """Like for the unlisted channel, an enterprise version can still be added
    to an addon disabled by its developer, and the addon stays disabled"""
    addon = create_addon(base_url, session_auth, 'enterprise')
    disable_addon = requests.patch(
        url=f'{base_url}{_addon_create}{addon["id"]}/',
        headers={'Authorization': f'Session {session_auth}'},
        json={'is_disabled': True},
    )
    assert (
        disable_addon.status_code == 200
    ), f'Actual response: {disable_addon.status_code}, {disable_addon.text}'
    uuid = valid_upload(base_url, session_auth, 'enterprise', addon['guid'], '1.1')
    new_version = create_version(base_url, session_auth, addon['id'], {'upload': uuid})
    assert (
        new_version.status_code == 201
    ), f'Actual response: {new_version.status_code}, {new_version.text}'
    assert new_version.json()['channel'] == 'enterprise'
    addon_detail = api_get(f'{base_url}{_addon_create}{addon["id"]}/', session_auth)
    assert addon_detail.json()['is_disabled'] is True


# TC-SG-04
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_delete_enterprise_version(base_url, session_auth):
    """A deleted enterprise version disappears from the enterprise_only
    filter and its version number can't be used again"""
    addon = create_addon(base_url, session_auth, 'enterprise')
    uuid = valid_upload(base_url, session_auth, 'enterprise', addon['guid'], '1.1')
    new_version = create_version(base_url, session_auth, addon['id'], {'upload': uuid})
    assert (
        new_version.status_code == 201
    ), f'Actual response: {new_version.status_code}, {new_version.text}'
    delete_version = requests.delete(
        url=f'{base_url}{_addon_create}{addon["id"]}/versions/{new_version.json()["id"]}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        delete_version.status_code == 204
    ), f'Actual response: {delete_version.status_code}, {delete_version.text}'
    enterprise_versions = addon_versions(base_url, session_auth, addon['id'], 'enterprise_only')
    assert [version['version'] for version in enterprise_versions] == ['1.0']
    uuid = valid_upload(base_url, session_auth, 'enterprise', addon['guid'], '1.1')
    reused_version = create_version(base_url, session_auth, addon['id'], {'upload': uuid})
    assert (
        reused_version.status_code == 409
    ), f'Actual response: {reused_version.status_code}, {reused_version.text}'
    assert reused_version.json() == {
        'version': ['Version 1.1 was uploaded before and deleted.']
    }, f'Actual response was {reused_version.text}'


# ---------------------------------------------------------------------------
# Negative / Robustness
# ---------------------------------------------------------------------------


def make_large_enterprise_addon(path, file_sizes_mb):
    """Build an enterprise addon zip at `path` that also contains files of zeros
    with the given uncompressed sizes; zeros compress very well, so the
    archive stays small to upload while its uncompressed size is large"""
    manifest = enterprise_manifest(admin_install_only=True)
    chunk = b'\0' * 1024 * 1024
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('manifest.json', json.dumps(manifest))
        for index, size_mb in enumerate(file_sizes_mb):
            with zipf.open(f'large-file-{index}.bin', 'w', force_zip64=True) as large_file:
                for _ in range(size_mb):
                    large_file.write(chunk)
    return path


# TC-NG-02
@pytest.mark.parametrize(
    'file_sizes_mb, expected_error',
    [
        # FILE_UNZIP_SIZE_LIMIT is 100 MiB for a single file in the archive
        ([101], 'File exceeding size limit in archive: large-file-0.bin'),
        # MAX_ZIP_UNCOMPRESSED_SIZE is 250 MiB for the whole archive
        ([90, 90, 90], 'Uncompressed size is too large'),
    ],
    ids=['Single file over 100MB', 'Archive over 250MB uncompressed'],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_oversized_enterprise_addon(
    base_url, session_auth, tmp_path, file_sizes_mb, expected_error
):
    """Enterprise uploads over the uncompressed size limits fail validation
    with a size error instead of a server error"""
    addon_file = make_large_enterprise_addon(tmp_path / 'large-addon.zip', file_sizes_mb)
    upload = upload_addon(base_url, session_auth, 'enterprise', addon_file)
    assert upload.status_code == 201, f'Actual response: {upload.status_code}, {upload.text}'
    resp = wait_for_upload_processed(base_url, session_auth, upload.json()['uuid'])
    assert resp['valid'] is False
    errors = validation_errors(resp)
    assert any(expected_error in error for error in errors), f'Actual validation errors: {errors}'


# TC-NG-03
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_enterprise_submission_paths_return_no_server_errors(base_url, session_auth):
    """Regression check for mozilla/addons#16368 (500 error when uploading an
    enterprise addon): every enterprise submission path, valid or not,
    should answer without a server error"""
    guid = f'enterprise-api@{reusables.get_random_string(8)}'
    responses = {}
    # upload create, valid and invalid
    api_helpers.make_addon(enterprise_manifest(guid=guid, admin_install_only=True))
    responses['upload create (valid)'] = upload_addon(base_url, session_auth, 'enterprise')
    api_helpers.make_addon(enterprise_manifest(guid=guid))
    responses['upload create (invalid)'] = upload_addon(base_url, session_auth, 'enterprise')
    valid_uuid = responses['upload create (valid)'].json()['uuid']
    invalid_uuid = responses['upload create (invalid)'].json()['uuid']
    for uuid in (valid_uuid, invalid_uuid):
        wait_for_upload_processed(base_url, session_auth, uuid)
    # add-on create, with an invalid upload first and then with the valid one
    for name, uuid in (('invalid', invalid_uuid), ('valid', valid_uuid)):
        responses[f'add-on create ({name})'] = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={'Authorization': f'Session {session_auth}'},
            json={'version': {'upload': uuid}},
        )
    addon_id = responses['add-on create (valid)'].json()['id']
    # version create, then PUT for another new version
    uuid = valid_upload(base_url, session_auth, 'enterprise', guid, '1.1')
    responses['version create'] = create_version(base_url, session_auth, addon_id, {'upload': uuid})
    uuid = valid_upload(base_url, session_auth, 'enterprise', guid, '1.2')
    responses['PUT new version'] = put_addon(base_url, session_auth, guid, uuid)
    server_errors = {
        name: f'{response.status_code}: {response.text[:200]}'
        for name, response in responses.items()
        if response.status_code >= 500
    }
    assert not server_errors, f'Server errors: {server_errors}'
    assert {name: response.status_code for name, response in responses.items()} == {
        'upload create (valid)': 201,
        'upload create (invalid)': 201,
        'add-on create (invalid)': 400,
        'add-on create (valid)': 201,
        'version create': 201,
        'PUT new version': 200,
    }


# TC-NG-04
@pytest.mark.serial
@pytest.mark.create_session('regular_user')
def test_enterprise_upload_without_dev_agreement(base_url, session_auth):
    """A user who hasn't accepted the developer agreement can't upload on the
    enterprise channel, and gets the same error as on the unlisted channel"""
    require_valid_session(
        base_url, session_auth, 'regular_user', 'test_enterprise_only_filter_as_non_author'
    )
    api_helpers.make_addon(enterprise_manifest(admin_install_only=True))
    responses = {
        channel: upload_addon(base_url, session_auth, channel)
        for channel in ('enterprise', 'unlisted')
    }
    for channel, upload in responses.items():
        assert upload.status_code == 403, f'{channel}: {upload.status_code}, {upload.text}'
        assert (
            'Please read and accept our Firefox Add-on Distribution Agreement' in upload.text
        ), f'{channel}: {upload.text}'
    assert responses['enterprise'].json() == responses['unlisted'].json()
