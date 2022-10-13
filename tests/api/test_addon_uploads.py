import json
import time

import pytest
import requests

from api import payloads, api_helpers
from pages.desktop.frontend.home import Home
from scripts import reusables

# endpoints used in the upload tests
_upload = '/api/v5/addons/upload/'
_addon_create = '/api/v5/addons/addon/'


# The API upload tests are handling various valid and invalid upload scenarios.
# Thy also cover uploads for every addon type: extension, theme, language pack.

# API endpoints covered are:
# create a new upload: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#upload-create
# list created uploads: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#upload-list
# verify upload details: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#upload-detail
# create an upload using PUT: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#put-create-or-edit


@pytest.mark.serial
def test_unauthenticated_addon_upload(base_url):
    with open('sample-addons/unlisted-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
    assert upload.status_code == 401, f'Actual status code was {upload.status_code}'
    assert (
        'Authentication credentials were not provided.' in upload.text
    ), f'Actual response message was {upload.text}'


@pytest.mark.serial
def test_upload_addon_without_dev_agreement(base_url, selenium):
    """Try to upload add-on with a user that hasn't accepted the dev agreements"""
    amo = Home(selenium, base_url).open().wait_for_page_to_load()
    amo.login('regular_user')
    session_cookie = selenium.get_cookie('sessionid')
    with open('sample-addons/unlisted-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_cookie["value"]}'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
    assert upload.status_code == 403, f'Actual status code was {upload.status_code}'
    assert (
        'Please read and accept our Firefox Add-on Distribution Agreement as well as our Review Policies and Rules'
        in upload.text
    ), f'Actual response message was {upload.text}'


@pytest.mark.serial
@pytest.mark.login('api_user')
def test_bad_authentication_addon_upload(selenium, base_url):
    with open('sample-addons/unlisted-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session q7e50318gibhehbw1gl1k57ofckb4f94'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
    assert upload.status_code == 401, f'Actual status code was {upload.status_code}'
    assert (
        'Valid user session not found matching the provided session key.","code":"ERROR_AUTHENTICATION_EXPIRED"'
        in upload.text
    ), f'Actual response message was {upload.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_addon_crx_archive(base_url, session_auth):
    """Use a .crx file to upload an addon and make sure the submission is successful"""
    with open('sample-addons/crx_ext.crx', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
    time.sleep(3)
    upload.raise_for_status()
    uuid = upload.json()['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    create_addon.raise_for_status()
    assert (
        create_addon.status_code == 201
    ), f'Actual response: {create_addon.status_code}, {create_addon.text}'


@pytest.mark.parametrize(
    'file_type',
    [
        '7z-ext.7z',
        'tgz-ext.tgz',
        'tar-gz-ext.tar.gz',
        'manifest.json',
    ],
    ids=[
        'Archive in "7z" format',
        'Archive in "tgz" format',
        'Archive in "tar.gz" format',
        'Non archive - JSON file',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_addon_unsupported_file_types(base_url, session_auth, file_type):
    """Try to upload unsupported archive types or files as extensions; AMO is supporting
    only three file types for addon uploads: .zip, .xpi, .crx"""
    with open(f'sample-addons/{file_type}', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
    time.sleep(3)
    upload.raise_for_status()
    uuid = upload.json()['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
    # get the validation messages returned by the API
    validation = requests.get(
        url=f'{base_url}{_upload}{uuid}',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        'Unsupported file type, please upload a supported file (.crx, .xpi, .zip).'
        in validation.json()['validation']['messages'][0]['message']
    ), f'Actual response for "{file_type}" was {validation.json()["validation"]}'


@pytest.mark.parametrize(
    'file_type',
    [
        'tar-renamed-as-zip.zip',
        'broken-archive.zip',
    ],
    ids=[
        'A "tar" compression renamed as "zip"',
        'Corrupt archive',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_addon_with_broken_archives(base_url, session_auth, file_type):
    """Try to upload an addon with a corrupt or invalid archive and check that the
    validation message identifies them as such; for example, a 'tar' compression
    renamed to look as a 'zip' file should be detected as invalid"""
    with open(f'sample-addons/{file_type}', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
    time.sleep(3)
    upload.raise_for_status()
    uuid = upload.json()['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
    # get the validation messages returned by the API
    validation = requests.get(
        url=f'{base_url}{_upload}{uuid}',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        'Invalid or corrupt add-on file.'
        in validation.json()['validation']['messages'][0]['message']
    ), f'Actual response for "{file_type}" was {validation.json()["validation"]}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_unlisted_extension(base_url, session_auth):
    with open('sample-addons/unlisted-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
    upload.raise_for_status()
    resp = upload.json()
    # print the response for debugging purposes
    print(json.dumps(resp, indent=2))
    assert 'unlisted' in resp['channel']
    # get the addon uuid generated after upload
    uuid = resp['uuid']
    data = {'version': {'upload': uuid}}
    # sleep to allow the first request to be processed
    time.sleep(5)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(data),
    )
    create_addon.raise_for_status()
    resp = create_addon.json()
    print(json.dumps(resp, indent=2))
    # verify the addon status ("incomplete" for unlisted)
    assert 'incomplete' in resp['status']
    # get the edit url for the add-on to verify that it was created and visible in devhub
    r = requests.get(resp['edit_url'], cookies={'sessionid': session_auth}, timeout=10)
    assert r.status_code == 200


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_submit_extension_with_invalid_uuid_format(base_url, session_auth):
    """The UUID format doesn't match the expected format for the uuid value"""
    uuid = [
        'some-invalid-uuid',
        {'upload': 'd4ce752a971b4a5aafcd175122726431'},
        None,
        '',
    ]
    for item in uuid:
        data = {'version': {'upload': item}}
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(data),
        )
        # capture the response details to ease debugging
        print(
            f'For UUID "{item}": Response status is '
            f'{create_addon.status_code}; {create_addon.text}\n'
        )
        # verify the status code and the response message for each value sent
        assert (
            create_addon.status_code == 400
        ), f'Actual status code was {create_addon.status_code}'
        if item is None or item == '':
            assert (
                'This field may not be null.' in create_addon.text
            ), f'Actual response message was {create_addon.text}'
        else:
            assert (
                f'“{item}” is not a valid UUID' in create_addon.text
            ), f'Actual response was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_submit_extension_with_incorrect_uuid(base_url, session_auth):
    """The UUID format is accepted but there is no valid upload found for the given uuid"""
    uuid = ['d4ce752a971b4a5aafcd175122726431', 12345]
    for item in uuid:
        data = {'version': {'upload': item}}
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(data),
        )
        print(
            f'For UUID "{item}": Response status is '
            f'{create_addon.status_code}; {create_addon.text}\n'
        )
        assert (
            create_addon.status_code == 400
        ), f'Actual status code was {create_addon.status_code}'
        assert (
            f'Object with uuid={item} does not exist.' in create_addon.text
        ), f'Actual response was {create_addon.text}'


@pytest.mark.parametrize(
    'trademark_name',
    [
        'Firefox in addon name',
        'Mozilla in addon name',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_submit_xpi_with_trademark_restricted_user(
    base_url, session_auth, trademark_name
):
    """Upload an addon that includes the 'Firefox' or 'Mozilla' names;
    regular users are not allowed to submit such addons"""
    # create a minimal manifest with a trademark name
    manifest = {**payloads.minimal_manifest, 'name': trademark_name}
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={"Authorization": f"Session {session_auth}"},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    resp = upload.json()
    # sleep to allow the upload  request to be processed
    time.sleep(3)
    uuid = resp['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual status code was {create_addon.status_code}'
    assert (
        'Add-on names cannot contain the Mozilla or Firefox trademarks.'
        in create_addon.text
    ), f'Actual response was {create_addon.text}'


@pytest.mark.parametrize(
    'guid',
    [
        'reserved_guid@mozilla.com',
        'reserved_guid@mozilla.org',
        'reserved_guid@pioneer.mozilla.org',
        'reserved_guid@search.mozilla.org',
        'reserved_guid@shield.mozilla.com',
        'reserved_guid@shield.mozilla.org',
        'reserved_guid@mozillaonline.com',
        'reserved_guid@mozillafoundation.org',
        'reserved_guid@rally.mozilla.org',
        'reserved_guid@temporary-addon',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_submit_addon_with_reserved_guid(base_url, session_auth, guid):
    """Upload an addon that has a reserved guid suffix, unavailable for regular users"""
    manifest = {
        **payloads.minimal_manifest,
        'name': 'Reserved guid',
        'browser_specific_settings': {'gecko': {'id': guid}},
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    # sleep to allow the upload  request to be processed
    time.sleep(3)
    resp = upload.json()
    print(resp)
    uuid = resp['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    print(
        f'For guid "{guid}": response status was {create_addon.status_code}, {create_addon.text}'
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual status code was {create_addon.status_code}'
    assert (
        'You cannot submit an add-on using an ID ending with this suffix'
        in create_addon.text
    ), f'Actual response was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_with_duplicate_guid(base_url, session_auth, variables):
    """Addon guids are unique and cannot be re-used for new addon submissions"""
    guid = variables['duplicate_guid']
    # make an add-on with an already existing guid
    manifest = {
        **payloads.minimal_manifest,
        'name': 'Duplicate guid',
        'browser_specific_settings': {'gecko': {'id': guid}},
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    resp = upload.json()
    uuid = resp['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual status code was {create_addon.status_code}'
    assert (
        'Duplicate add-on ID found.' in create_addon.text
    ), f'Actual message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_without_name_in_manifest(base_url, session_auth):
    """The 'name' key is mandatory for successful submissions; uploading an
    addon with a manifest that misses a 'name' key should fail"""
    # create a manifest that doesn't include the mandatory 'name' key
    manifest = {**payloads.minimal_manifest}
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    resp = upload.json()
    print(resp)
    uuid = resp['uuid']
    # we need to inspect the validation results returned by the linter
    # to check if the 'name' field has produced a validation error
    get_upload_details = requests.get(
        url=f'{base_url}{_upload}{uuid}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    error = get_upload_details.json()
    # pull the validation messages and check the 'name' field error
    assert (
        'must have required property \'name\''
        in error['validation']['messages'][0]['message']
    )
    payload = payloads.listed_addon_minimal(uuid)
    # try to upload the add-on without a name anyway; it should fail
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual status code was {create_addon.status_code}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_without_summary(base_url, session_auth):
    """An addon summary is mandatory for successful submissions; uploading an addon without a
    'description' key and no 'summary' included in the JSON payload should fail"""
    # create a minimal manifest, without adding a 'description' field
    manifest = {**payloads.minimal_manifest, 'name': 'Addon without Summary'}
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    resp = upload.json()
    print(resp)
    uuid = resp['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    # try to upload the addon without a summary anyway; it should fail
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual status code was {create_addon.status_code}'
    assert (
        '{"summary":["This field is required for add-ons with listed versions."]}'
        in create_addon.text
    ), f'Actual message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_with_incorrect_version_number(base_url, session_auth):
    """The addon version number is defined in the manifest and needs to follow some naming rules"""
    # create a minimal manifest, with an invalid 'version'
    manifest = {
        **payloads.minimal_manifest,
        'name': 'Addon with invalid version',
        'version': '1abc.1.1a#c',
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    resp = upload.json()
    uuid = resp['uuid']
    # we need to inspect the validation results returned by the linter
    # to check if the 'version' field has produced a validation error
    get_upload_details = requests.get(
        url=f'{base_url}{_upload}{uuid}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    error = get_upload_details.json()
    # check the upload validation results for 'version' field errors
    assert (
        '"/version" must match format "versionString"'
        in error['validation']['messages'][0]['message']
    )
    payload = payloads.listed_addon_minimal(uuid)
    # try to upload the add-on with the invalid version; it should fail
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual status code was {create_addon.status_code}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_with_put_method(base_url, session_auth):
    """Use the PUT method to create a new addon; unlike POST,
    PUT requires the addon guid to be specified in the request"""
    guid = f'random-guid@{reusables.get_random_string(6)}'
    name = (
        f'PUT-create-addon-{reusables.get_random_string(6)}-{reusables.current_date()}'
    )
    # create the addon manifest to be uploaded
    manifest = {
        **payloads.minimal_manifest,
        'name': name,
        'browser_specific_settings': {'gecko': {'id': guid}},
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    resp = upload.json()
    print(resp)
    uuid = resp['uuid']
    payload = {
        **payloads.listed_addon_minimal(uuid),
        'summary': {'en-US': 'Addon summary'},
    }
    create_addon = requests.put(
        url=f'{base_url}{_addon_create}{guid}/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    response = create_addon.json()
    print(json.dumps(response, indent=2))
    # check that the addon was created with the guid set
    assert response['guid'] == guid


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_with_put_guid_mismatch(base_url, session_auth):
    """The PUT method requires the same guid to be specified in the manifest and in the request url;
    this test verifies that the submission fails if there is a guid mismatch between the two"""
    guid = f'random-guid@{reusables.get_random_string(6)}'
    # create the addon manifest to be uploaded
    manifest = {
        **payloads.minimal_manifest,
        'name': 'PUT-guid-mismatch',
        'browser_specific_settings': {'gecko': {'id': guid}},
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    resp = upload.json()
    print(resp)
    uuid = resp['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.put(
        url=f'{base_url}{_addon_create}mismatch-guid@foobar/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual status code was {create_addon.status_code}'
    assert (
        'GUID mismatch between the URL and manifest.' in create_addon.text
    ), f'Actual message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_with_put_no_guid_in_manifest(base_url, session_auth):
    """The PUT method requires a guid to be specified in the manifest;
    if no guid is specified, the request should fail"""
    with open('sample-addons/listed-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    resp = upload.json()
    print(resp)
    uuid = resp['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.put(
        url=f'{base_url}{_addon_create}manifest-no-guid@foobar/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual status code was {create_addon.status_code}'
    assert (
        'A GUID must be specified in the manifest.' in create_addon.text
    ), f'Actual message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_with_put_no_guid_in_request(base_url, session_auth):
    """The PUT method requires a guid to be specified in the request;
    if no guid is specified in the url, the request should fail"""
    guid = f'random-guid@{reusables.get_random_string(6)}'
    # create the addon manifest to be uploaded
    manifest = {
        **payloads.minimal_manifest,
        'name': 'PUT-no-guid-in-request-url',
        'browser_specific_settings': {'gecko': {'id': guid}},
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    resp = upload.json()
    uuid = resp['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.put(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    # the request sent is valid with a POST request; with PUT is not accepted
    assert (
        create_addon.status_code == 405
    ), f'Actual status code was {create_addon.status_code}'
    assert (
        'Method \\"PUT\\" not allowed.' in create_addon.text
    ), f'Actual message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_with_put_invalid_guid_format(base_url, session_auth):
    """Uploading an addon with an invalid guid format should fail the PUT request"""
    guid = f'invalid-{reusables.get_random_string(6)}'  # creates an invalid guid
    manifest = {
        **payloads.minimal_manifest,
        'name': 'Invalid guid format',
        'browser_specific_settings': {'gecko': {'id': guid}},
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    resp = upload.json()
    print(resp)
    uuid = resp['uuid']
    # check that the upload validation results point at a faulty guid
    get_upload_details = requests.get(
        url=f'{base_url}{_upload}{uuid}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    error = get_upload_details.json()
    assert (
        '/browser_specific_settings/gecko/id'
        in error['validation']['messages'][0]['instancePath']
    )
    # try to submit the addon with an invalid guid anyway; it should fail
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.put(
        url=f'{base_url}{_addon_create}{guid}/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 404
    ), f'Actual status code was {create_addon.status_code}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_default_locale_has_no_translations(base_url, session_auth):
    """Try to upload an addon while setting a 'default_locale' for which there are no
    available translations in the mandatory fields, i.e. 'name' and 'summary'"""
    with open('sample-addons/localizations.xpi', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    # sleep to allow the first request to be processed
    time.sleep(3)
    upload.raise_for_status()
    resp = upload.json()
    # get the addon uuid generated after upload
    uuid = resp['uuid']
    slug = reusables.get_random_string(10)
    # set a default locale that doesn't have any translations in the xpi or the request JSON
    payload = {
        **payloads.listed_addon_minimal(uuid),
        'slug': slug,
        'default_locale': 'ja',
    }
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual status code was {create_addon.status_code}'
    # check that the error reflects that 'name' and 'summary' are mandatory fields to set a 'default_locale'
    assert (
        create_addon.text
        == '{"name":["A value in the default locale of \\"ja\\" is required."],'
        '"summary":["A value in the default locale of \\"ja\\" is required."]}'
    )


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_with_localizations_in_xpi(base_url, session_auth, variables):
    """Addon translations set in a 'locales' file in the .xpi should be reflected
    in the API response returned after the addon is successfully created"""
    with open('sample-addons/localizations.xpi', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    # sleep to allow the first request to be processed
    time.sleep(3)
    resp = upload.json()
    upload.raise_for_status()
    # get the addon uuid generated after upload
    uuid = resp['uuid']
    # set a unique addon slug to make sure we don't run into duplicates
    slug = reusables.get_random_string(10)
    payload = {**payloads.listed_addon_minimal(uuid), 'slug': slug}
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    create_addon.raise_for_status()
    response = create_addon.json()
    # verify that the translations from the xpi are reflected in the api response
    assert response['default_locale'] == 'de'
    assert response['name'] == variables['name_translations_from_locales_xpi']
    assert response['summary'] == variables['summary_translations_from_locales_xpi']


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_localized_extension_json_overwrite(base_url, session_auth):
    """If an addon with a 'locales' file defined in the .xpi sets different translations
    in the request JSON object, the JSON values should override the locales file from the .xpi"""
    with open('sample-addons/localizations.xpi', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    # sleep to allow the first request to be processed
    time.sleep(3)
    upload.raise_for_status()
    resp = upload.json()
    # get the addon uuid generated after upload
    uuid = resp['uuid']
    # set a unique addon slug to make sure we don't run into duplicates
    slug = reusables.get_random_string(10)
    payload = {
        **payloads.listed_addon_details(uuid),
        'slug': slug,
        'default_locale': 'en-US',
    }
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    create_addon.raise_for_status()
    response = create_addon.json()
    # verify that xpi translations have been overwritten by the JSON payload translations
    assert response['default_locale'] == payload['default_locale']
    assert response['name'] == payload['name']
    assert response['summary'] == payload['summary']


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_addon_with_guid_from_deleted_addon(base_url, session_auth):
    """Create an addon, delete it and then try to reuse the GUID to submit a
    new addon; the request should fail since GUIDs cannot be reused"""
    guid = f'reused-guid@{reusables.get_random_string(6)}'
    # create the addon manifest to be uploaded
    manifest = {
        **payloads.minimal_manifest,
        'name': 'Reuse GUID of deleted addon',
        'browser_specific_settings': {'gecko': {'id': guid}},
    }
    api_helpers.make_addon(manifest)
    # upload the addon with the custom GUID for the first time
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
    time.sleep(3)
    upload.raise_for_status()
    uuid = upload.json()['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    create_addon.raise_for_status()
    # get the token that would allow the actual delete request to be sent
    get_delete_confirm = requests.get(
        url=f'{base_url}{_addon_create}{guid}/delete_confirm/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    token = get_delete_confirm.json()['delete_confirm']
    # delete the addon and verify that the delete request was successful
    delete_addon = requests.delete(
        url=f'{base_url}{_addon_create}{guid}/',
        headers={'Authorization': f'Session {session_auth}'},
        params={'delete_confirm': token},
    )
    assert (
        delete_addon.status_code == 204
    ), f'Actual response: {delete_addon.status_code}, {delete_addon.text}'
    # upload the addon using the same custom GUID for the second time
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    time.sleep(3)
    upload.raise_for_status()
    uuid = upload.json()['uuid']
    payload = payloads.listed_addon_minimal(uuid)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    # verify that the submission fails because it uses a duplicate GUID
    assert (
        create_addon.status_code == 400
    ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
    assert (
        'Duplicate add-on ID found.' in create_addon.text
    ), f'Actual message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_theme(base_url, session_auth):
    with open('sample-addons/theme.xpi', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
        time.sleep(3)
        upload.raise_for_status()
        # get the addon uuid generated after upload
        uuid = upload.json()['uuid']
        # set a license type specific for themes
        theme_license = 'CC-BY-3.0'
        payload = {
            **payloads.theme_details(uuid, theme_license),
            'slug': f'theme-{reusables.get_random_string(10)}',
        }
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        create_addon.raise_for_status()
        # verify that the addon has been submitted as a theme by checking the 'type' property
        assert create_addon.json()['type'] == 'statictheme'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_theme_with_wrong_license(base_url, session_auth):
    """Try to upload a theme while using a license that is specific for extensions"""
    with open('sample-addons/theme.xpi', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
        time.sleep(3)
        upload.raise_for_status()
        # get the addon uuid generated after upload
        uuid = upload.json()['uuid']
        # set a license slug that is allowed only for extension submissions
        ext_license = 'MPL-2.0'
        payload = {
            **payloads.theme_details(uuid, ext_license),
            'slug': f'theme-{reusables.get_random_string(10)}',
        }
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        assert (
            create_addon.status_code == 400
        ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
        assert (
            'Wrong add-on type for this license.' in create_addon.text
        ), f'Actual response was {create_addon.text}'


@pytest.mark.serial
def test_upload_language_pack_unauthorized_user(selenium, base_url):
    """Users not part of the language pack submission group are not allowed to submit langpacks"""
    # get the sessionid for a regular user
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login('developer')
    session_auth = selenium.get_cookie('sessionid')
    with open('sample-addons/lang-pack.xpi', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth["value"]}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    time.sleep(3)
    upload.raise_for_status()
    # get the addon uuid generated after upload
    uuid = upload.json()['uuid']
    payload = payloads.lang_tool_details(uuid)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth["value"]}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
    assert (
        'You cannot submit a language pack' in create_addon.text
    ), f'Actual response message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_language_pack_with_authorized_user(base_url, session_auth):
    """Upload a langpack with a user that belongs to the language pack submissions group"""
    with open('sample-addons/lang-pack.xpi', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    time.sleep(3)
    upload.raise_for_status()
    # get the addon uuid generated after upload
    uuid = upload.json()['uuid']
    payload = payloads.lang_tool_details(uuid)
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 201
    ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
    response = create_addon.json()
    # verify that the add-on was created as a language pack by looking at the 'type' property
    assert response['type'] == 'language'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_language_pack_incorrect_category(base_url, session_auth):
    """Language packs only accept 'general' as a category value; other values should fail"""
    with open('sample-addons/lang-pack.xpi', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'listed'},
        )
    time.sleep(3)
    upload.raise_for_status()
    # get the addon uuid generated after upload
    uuid = upload.json()['uuid']
    payload = {
        **payloads.lang_tool_details(uuid),
        'categories': {'firefox': ['bookmarks']},
    }
    create_addon = requests.post(
        url=f'{base_url}{_addon_create}',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
    assert (
        'Invalid category name.' in create_addon.text
    ), f'Actual response message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_privileged_addon_with_unauthorized_account(base_url, session_auth):
    """Upload an addon signed with a mozilla signature using an unauthorized account"""
    with open('sample-addons/mozilla-signed.xpi', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
        time.sleep(3)
        upload.raise_for_status()
        # get the addon uuid generated after upload
        uuid = upload.json()['uuid']
        payload = {**payloads.listed_addon_minimal(uuid)}
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        assert (
            create_addon.status_code == 400
        ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
        assert 'You cannot submit a Mozilla Signed Extension' in create_addon.text


@pytest.mark.serial
@pytest.mark.login('staff_user')
def test_upload_privileged_addon_with_authorized_account(selenium, base_url):
    """Upload an addon signed with a mozilla signature using an account holding the right permissions"""
    session_auth = selenium.get_cookie('sessionid')
    with open('sample-addons/mozilla-signed.xpi', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth["value"]}'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
        time.sleep(3)
        upload.raise_for_status()
        # get the addon uuid generated after upload
        uuid = upload.json()['uuid']
        payload = {**payloads.listed_addon_minimal(uuid)}
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth["value"]}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        assert (
            create_addon.status_code == 201
        ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
        # check that the addon was created as a mozilla signed addon
        assert (
            create_addon.json()['latest_unlisted_version']['file'][
                'is_mozilla_signed_extension'
            ]
            is True
        )


@pytest.mark.serial
@pytest.mark.create_session('staff_user')
def test_upload_addon_with_reserved_guid_authorized_account(base_url, session_auth):
    """Upload an addon with a reserved guid using an account that holds the right permissions"""
    # create a restricted GUID
    guid = f'{reusables.get_random_string(10)}@mozilla.org'
    manifest = {
        **payloads.minimal_manifest,
        'name': 'Reserved guid',
        'browser_specific_settings': {'gecko': {'id': guid}},
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
        time.sleep(3)
        upload.raise_for_status()
        # get the addon uuid generated after upload
        uuid = upload.json()['uuid']
        payload = {**payloads.listed_addon_minimal(uuid)}
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        print(create_addon.text)
        assert (
            create_addon.status_code == 201
        ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
        # check that the addon was created with the guid set
        assert create_addon.json()['guid'] == guid


@pytest.mark.serial
@pytest.mark.create_session('staff_user')
@pytest.mark.clear_session
def test_upload_addon_with_trademark_name_authorized_account(
    selenium, base_url, session_auth
):
    """Upload an addon that includes the 'Firefox' trademark name with a user that holds the right permissions"""
    # create an addon with a trademark name
    addon_name = 'Firefox trademark'
    manifest = {
        **payloads.minimal_manifest,
        'name': addon_name,
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={'Authorization': f'Session {session_auth}'},
            files={'upload': file},
            data={'channel': 'unlisted'},
        )
        time.sleep(3)
        upload.raise_for_status()
        uuid = upload.json()['uuid']
        payload = payloads.listed_addon_minimal(uuid)
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        # verify that the addon was created successfully
        assert (
            create_addon.status_code == 201
        ), f'Actual response: {create_addon.status_code}, {create_addon.text}'
        assert addon_name == create_addon.json()['name']['en-US']
