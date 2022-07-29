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


@pytest.mark.serial
def test_unauthenticated_addon_upload(base_url):
    upload = requests.post(
        url=f'{base_url}{_upload}',
        files={"upload": open('sample-addons/unlisted-addon.zip', 'rb')},
        data={"channel": "unlisted"},
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
    upload = requests.post(
        url=f'{base_url}{_upload}',
        headers={'Authorization': f'Session {session_cookie["value"]}'},
        files={"upload": open('sample-addons/unlisted-addon.zip', 'rb')},
        data={"channel": "unlisted"},
    )
    assert upload.status_code == 403, f'Actual status code was {upload.status_code}'
    assert (
        'Please read and accept our Firefox Add-on Distribution Agreement as well as our Review Policies and Rules'
        in upload.text
    ), f'Actual response message was {upload.text}'


@pytest.mark.serial
@pytest.mark.login('api_user')
def test_bad_authentication_addon_upload(selenium, base_url):
    upload = requests.post(
        url=f'{base_url}{_upload}',
        headers={"Authorization": f"Session q7e50318gibhehbw1gl1k57ofckb4f94"},
        files={"upload": open('sample-addons/unlisted-addon.zip', 'rb')},
        data={"channel": "unlisted"},
    )
    assert upload.status_code == 401, f'Actual status code was {upload.status_code}'
    assert (
        'Valid user session not found matching the provided session key.","code":"ERROR_AUTHENTICATION_EXPIRED"'
        in upload.text
    ), f'Actual response message was {upload.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_unlisted_extension(base_url, session_auth):
    upload = requests.post(
        url=f'{base_url}{_upload}',
        headers={"Authorization": f"Session {session_auth}"},
        files={"upload": open('sample-addons/unlisted-addon.zip', 'rb')},
        data={"channel": "unlisted"},
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
            "Content-Type": "application/json",
        },
        data=json.dumps(data),
    )
    create_addon.raise_for_status()
    resp = create_addon.json()
    print(json.dumps(resp, indent=2))
    # verify the addon status ("incomplete" for unlisted)
    assert 'incomplete' in resp['status']
    # get the edit url for the add-on to verify that it was created and visible in devhub
    r = requests.get(resp['edit_url'], cookies={"sessionid": session_auth}, timeout=10)
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
            data={"channel": "listed"},
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
            "Content-Type": "application/json",
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
        'browser_specific_settings': {"gecko": {"id": guid}},
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={"Authorization": f"Session {session_auth}"},
            files={'upload': file},
            data={"channel": "listed"},
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
            "Content-Type": "application/json",
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
def test_upload_listed_extension(base_url, session_auth):
    upload = requests.post(
        url=f'{base_url}{_upload}',
        headers={'Authorization': f'Session {session_auth}'},
        files={'upload': open('sample-addons/listed-addon.zip', 'rb')},
        data={'channel': 'listed'},
    )
    resp = upload.json()
    print(json.dumps(resp, indent=2))
    upload.raise_for_status()
    assert 'listed' in resp['channel']
    # get the addon uuid generated after upload
    uuid = resp['uuid']
    payload = payloads.listed_addon_details(uuid)
    # sleep to allow the first request to be processed
    time.sleep(5)
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
    print(json.dumps(response, indent=2))
    # verify that the data we sent has been registered correctly in the response we get
    api_helpers.verify_addon_response_details(payload, response, 'create')


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_upload_extension_with_duplicate_guid(base_url, session_auth):
    """Addon guids are unique and cannot be re-used for new addon submissions"""
    # get the guid of the addon submitted previously
    get_upload_details = requests.get(
        url=f'{base_url}{_addon_create}my_sluggish_slug/',
        headers={"Authorization": f"Session {session_auth}"},
    )
    guid = get_upload_details.json()['guid']
    # make an add-on with an already existing guid
    manifest = {
        **payloads.minimal_manifest,
        'name': 'Duplicate guid',
        'browser_specific_settings': {"gecko": {"id": guid}},
    }
    api_helpers.make_addon(manifest)
    with open('sample-addons/make-addon.zip', 'rb') as file:
        upload = requests.post(
            url=f'{base_url}{_upload}',
            headers={"Authorization": f"Session {session_auth}"},
            files={'upload': file},
            data={"channel": "listed"},
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
            "Content-Type": "application/json",
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
def test_edit_listed_addon_details(base_url, session_auth):
    payload = payloads.edit_addon_details
    edit_addon = requests.patch(
        url=f'{base_url}{_addon_create}my_sluggish_slug/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    edit_addon.raise_for_status()
    response = edit_addon.json()
    print(json.dumps(response, indent=2))
    # verify that the data we sent has been registered correctly in the response we get
    api_helpers.verify_addon_response_details(payload, response, 'edit')


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_add_invalid_android_categories(base_url, session_auth):
    """Try to upload an addon that has invalid android categories set in the JSON payload"""
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
    print(upload.json())
    # get the addon uuid generated after upload
    uuid = upload.json()['uuid']
    invalid_android_catg = ['nature', 'privacy-security', '', 123, None]
    for item in invalid_android_catg:
        payload = {
            **payloads.listed_addon_details(uuid),
            'categories': {'android': [item], 'firefox': ['bookmarks']},
            'slug': 'invalid-android-cat',
        }
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        print(
            f'For android category "{item}": Response status is {create_addon.status_code}; {create_addon.text}\n'
        )
        assert (
            create_addon.status_code == 400
        ), f'Actual status code was {create_addon.status_code}'
        assert (
            'Invalid category name' in create_addon.text
        ), f'Actual response message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_add_invalid_firefox_categories(base_url, session_auth):
    """Try to upload an addon that has invalid firefox categories set in the JSON payload"""
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
    print(upload.json())
    # get the addon uuid generated after upload
    uuid = upload.json()['uuid']
    invalid_firefox_catg = ['fashion', 'security-privacy', '', 12.3]
    for item in invalid_firefox_catg:
        payload = {
            **payloads.listed_addon_details(uuid),
            'categories': {'android': ['performance'], 'firefox': [item]},
            'slug': 'invalid-firefox-cat',
        }
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        print(
            f'For firefox category "{item}": Response status is {create_addon.status_code}; {create_addon.text}\n'
        )
        assert (
            create_addon.status_code == 400
        ), f'Actual status code was {create_addon.status_code}'
        assert (
            'Invalid category name' in create_addon.text
        ), f'Actual response message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_other_category_is_standalone(base_url, session_auth):
    """Extensions with a category set to 'other' cannot have another category set"""
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
    print(upload.json())
    # get the addon uuid generated after upload
    uuid = upload.json()['uuid']
    payload = {
        **payloads.listed_addon_details(uuid),
        'categories': {
            'android': ['other', 'performance'],
            'firefox': ['other', 'bookmarks'],
        },
        'slug': 'other-category',
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
    assert (
        'The \\"other\\" category cannot be combined with another category'
        in create_addon.text
    ), f'Actual response message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_invalid_slug(base_url, session_auth):
    """Addon slugs can be composed only from letters and numbers"""
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
    print(upload.json())
    # get the addon uuid generated after upload
    uuid = upload.json()['uuid']
    invalid_slugs = [102030, '---', '?name', '@#_' ')(', None]
    for item in invalid_slugs:
        # crete a new dictionary from the original payload, with invalid slug values
        payload = {**payloads.listed_addon_details(uuid), 'slug': item}
        create_addon = requests.post(
            url=f'{base_url}{_addon_create}',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        print(
            f'For slug "{item}": Response status is {create_addon.status_code}; {create_addon.text}\n'
        )
        assert (
            create_addon.status_code == 400
        ), f'Actual status code was {create_addon.status_code}'
        if item == invalid_slugs[0]:  # slugs cannot contain only digits either
            assert (
                'This slug cannot be used. Please choose another.' in create_addon.text
            ), f'Actual response message was {create_addon.text}'
        else:
            assert (
                'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.'
                in create_addon.text
            ), f'Actual response message was {create_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_duplicate_slug(base_url, session_auth, variables):
    """Use a slug that already belongs to another addon"""
    addon = payloads.edit_addon_details['slug']
    payload = {
        **payloads.edit_addon_details,
        'slug': variables['approved_addon_with_sources'],
    }
    edit_addon = requests.patch(
        url=f'{base_url}{_addon_create}{addon}/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        edit_addon.status_code == 400
    ), f'Actual status code was {edit_addon.status_code}'
    assert (
        'addon with this slug already exists.' in edit_addon.text
    ), f'Actual response message was {edit_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_invalid_name(base_url, session_auth):
    """Addon names are required to have at least one letter or number character to be valid"""
    addon = payloads.edit_addon_details['slug']
    invalid_names = ['', '.', '****', None]
    for item in invalid_names:
        # crete a new dictionary from the original payload, with invalid name values
        payload = {**payloads.edit_addon_details, 'name': {'en-US': item}}
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        print(
            f'For name "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f'Actual status code was {edit_addon.status_code}'
        # check response messages based on the name value sent
        if item == '':
            assert (
                'This field may not be blank' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        elif item is None:
            assert (
                'A value in the default locale of \\"en-US\\" is required.'
                in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        else:
            assert (
                'Ensure this field contains at least one letter or number character'
                in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'


@pytest.mark.parametrize(
    'trademark_name',
    [
        'A Name with Firefox',
        'A Name with Mozilla',
        'A Name with Mozilla Firefox',
        'Name has FireFox',
        'Name has MOZILLA',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_with_trademark_in_name(base_url, session_auth, trademark_name):
    """Verifies that addon names can't be edited to include a Mozilla or Firefox trademark"""
    addon = payloads.edit_addon_details['slug']
    # crete a new dictionary from the original payload, with variable name values
    name = {**payloads.edit_addon_details, 'name': {'en-US': trademark_name}}
    edit_addon = requests.patch(
        url=f'{base_url}{_addon_create}{addon}/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(name),
    )
    print(
        f'For name "{trademark_name}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
    )
    assert (
        edit_addon.status_code == 400
    ), f'Actual status code was {edit_addon.status_code}'
    # check that the trademark check error message is returned
    assert (
        'Add-on names cannot contain the Mozilla or Firefox trademarks.'
        in edit_addon.text
    ), f'Actual response message was {edit_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_invalid_summary(base_url, session_auth):
    """Addon summaries need to be in string format and below 250 characters"""
    addon = payloads.edit_addon_details['slug']
    over_250_summary = reusables.get_random_string(251)
    summaries = ['', over_250_summary, None]
    # crete a new dictionary from the original payload, with invalid summary values
    for item in summaries:
        payload = {**payloads.edit_addon_details, 'summary': {'en-US': item}}
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        print(
            f'For summary "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f'Actual status code was {edit_addon.status_code}'
        # check response messages based on the summary value sent
        if item == '':
            assert (
                'This field may not be blank.' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        elif item == over_250_summary:
            assert (
                'Ensure this field has no more than 250 characters.' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        else:  # if None
            assert (
                'A value in the default locale of \\"en-US\\" is required.'
                in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_invalid_homepage(base_url, session_auth):
    """Try to add some invalid and unaccepted homepage urls for an addon"""
    addon = payloads.edit_addon_details['slug']
    invalid_homepage = [
        '',
        '.',
        'abc123',
        'example.com',
        'http://not-valid',
        'www.some-url.org',
        base_url,
    ]
    for item in invalid_homepage:
        # crete a new dictionary from the original payload, with variable homepage values
        homepage = {**payloads.edit_addon_details, 'homepage': {'en-US': item}}
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(homepage),
        )
        print(
            f'For homepage "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f'Actual status code was {edit_addon.status_code}'
        # check response messages based on the homepage value sent
        if item == '':
            assert (
                'This field may not be blank' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        # homepage URLs can't belong to the AMO domains
        elif item == base_url:
            assert (
                f'This field can only be used to link to external websites. URLs on {base_url} are not allowed.'
                in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        else:
            assert (
                'Enter a valid URL.' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_invalid_support_email(base_url, session_auth):
    """Try to add some invalid and unaccepted emails for an addon"""
    addon = payloads.edit_addon_details['slug']
    invalid_email = ['', '.', 'abc123', 'mail.com', 'abc@defg', 123, None]
    for item in invalid_email:
        # crete a new dictionary from the original payload, with variable email values
        email = {**payloads.edit_addon_details, 'support_email': {'en-US': item}}
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(email),
        )
        print(
            f'For email "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f'Actual status code was {edit_addon.status_code}'
        # check response messages based on the email value sent
        if item == '':
            assert (
                'This field may not be blank' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        elif item is None:
            assert (
                'A value in the default locale of \\"en-US\\" is required if other translations are set.'
                in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        else:
            assert (
                'Enter a valid email address.' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_invalid_experimental_and_payment(base_url, session_auth):
    """Try to set the 'experimental' and 'requires_payment' fields to other values than boolean"""
    addon = payloads.edit_addon_details['slug']
    # 'is_experimental' and 'requires_payment' can only be True or False
    invalid_values = ['', 'abc123', None, 123]
    for item in invalid_values:
        # crete a new dictionary from the original payload, with variable values
        payload = {
            **payloads.edit_addon_details,
            'is_experimental': item,
            'requires_payment': item,
        }
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        print(
            f'For email "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f'Actual status code was {edit_addon.status_code}'
        # check response messages based on the values sent
        if item is None:
            assert (
                'This field may not be null.' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        else:
            assert (
                'Must be a valid boolean.' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_valid_contribute_domains(base_url, session_auth):
    """Add a valid contributions url to an addon; requests should be successful"""
    addon = payloads.edit_addon_details['slug']
    valid_domains = [
        'https://www.buymeacoffee.com',
        'https://donate.mozilla.org',
        'https://flattr.com',
        'https://github.com/sponsors/',
        'https://ko-fi.com',
        'https://liberapay.com',
        'https://www.micropayment.de',
        'https://opencollective.com',
        'https://www.patreon.com',
        'https://www.paypal.com',
        'https://paypal.me',
    ]
    for item in valid_domains:
        # crete a new dictionary from the original payload, with variable domain values
        payload = {**payloads.edit_addon_details, 'contributions_url': item}
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        print(
            f'For domain "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 200
        ), f'Actual status code was {edit_addon.status_code}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_invalid_contribute_domains(base_url, session_auth, variables):
    """Set an invalid or an unaccepted value as the addon's contribution url;
    accepted domains are predefined and must all start with 'https'"""
    addon = payloads.edit_addon_details['slug']
    invalid_domains = [
        '',
        123,
        'abc123',
        'https://invalid.com',
        'https://www.notbuymeacoffee.com',
        'http://donate.mozilla.org',
        'https://patreon.com',
        'https://www.paypal.me',
    ]
    for item in invalid_domains:
        # crete a new dictionary from the original payload, with variable domain values
        payload = {**payloads.edit_addon_details, 'contributions_url': item}
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        print(
            f'For domain "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f'Actual status code was {edit_addon.status_code}'
        # check response messages based on the domain value sent
        if item == '':
            assert (
                'This field may not be blank' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        # domain starts with 'https' but is not in the accepted domains list
        elif type(item) is str and item.startswith('https://'):
            assert (
                variables['contributions_bad_request_message'] in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        # domain is in the accepted list but starts with 'http'
        elif item == 'http://donate.mozilla.org':
            assert (
                'URLs must start with https://.' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        else:
            # if the value doesn't start with 'https' and is not in the accepted list
            assert (
                variables['contributions_bad_request_message']
                and 'URLs must start with https://.' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_invalid_addon_tags(base_url, session_auth):
    """Try to set some invalid or unaccepted tags to an addon; valid tags are predefined"""
    addon = payloads.edit_addon_details['slug']
    # set some invalid or combinations of invalid tags; for example,
    # a combination of a valid and an invalid tag should not be accepted
    invalid_tags = [['', 'abc123'], None, [123, 'search'], True]
    for item in invalid_tags:
        # crete a new dictionary from the original payload, with variable values
        payload = {**payloads.edit_addon_details, 'tags': item}
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        print(
            f'For tags "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f'Actual status code was {edit_addon.status_code}'
        # check response messages based on the values sent
        if item is None:
            assert (
                'This field may not be null.' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        elif type(item) is list:  # items stored in list but are not valid tags
            assert (
                'is not a valid choice' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'
        else:  # if values are not stored in a list
            assert (
                'Expected a list of items' in edit_addon.text
            ), f'Actual response message was {edit_addon.text}'


@pytest.mark.parametrize(
    'icon',
    [
        'img/profile_picture.png',
        'img/addon_icon.jpg',
    ],
    ids=[
        'PNG icon',
        'JPG icon',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_add_valid_icon(base_url, session_auth, icon):
    """Upload a custom icon for an addon; JPG and PNG are the only accepted formats"""
    addon = payloads.edit_addon_details['slug']
    with open(icon, 'rb') as img:
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/',
            headers={'Authorization': f'Session {session_auth}'},
            files={'icon': img},
        )
        print(
            f'For icon "{icon}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 200
        ), f'Actual status code was {edit_addon.status_code}'
        # get the icons returned by the API and add them to a list (icons are saved in three sizes)
        r_icons = edit_addon.json()['icons']
        user_icons = [value for value in r_icons.values()]
        # if the icon has been upload successfully, we should se '/user-media/' in the icon location
        # and not '/static-server/' which is the location for the default icon served by AMO
        for icon in user_icons:
            assert f'{base_url}/user-media/addon_icons/' in icon


@pytest.mark.parametrize(
    'count, icon',
    enumerate(
        [
            'img/bmp_icon.bmp',
            'img/static_gif.gif',
            'img/animated_png.png',
            'img/invalid_image.png',
            'img/not_square.png',
        ]
    ),
    ids=[
        'BMP icon',
        'GIF static icon',
        'PNG animated icon',
        'Non image file with a .png extension',
        'Icon not square',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_add_invalid_icons(base_url, session_auth, count, icon, variables):
    """Verify that requests fail if icons do not meet these acceptance criteria:
    PNG or JPG, square images, non-animated images, valid image file"""
    addon = payloads.edit_addon_details['slug']
    with open(icon, 'rb') as img:
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/',
            headers={'Authorization': f'Session {session_auth}'},
            files={'icon': img},
        )
        print(
            f'For icon "{icon}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f'Actual status code was {edit_addon.status_code}'
        # check that the validation messages expected for each image type are matching the API response
        assert variables['image_validation_messages'][count] in edit_addon.text


@pytest.mark.parametrize(
    'count, preview',
    enumerate(
        [
            'img/screenshot_3.png',
            'img/screenshot_1.jpg',
        ]
    ),
    ids=[
        'PNG image',
        'JPG image',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_add_valid_screenshots(base_url, session_auth, count, preview):
    """Set valid preview images for an addon; only JPG and JPG formats are accepted"""
    addon = payloads.edit_addon_details['slug']
    with open(preview, 'rb') as img:
        edit_addon = requests.post(
            url=f'{base_url}{_addon_create}{addon}/previews/',
            headers={'Authorization': f'Session {session_auth}'},
            files={'image': img},
            data={
                'position': count
            },  # sets the order in which the previews should appear
        )
        print(
            f'For image "{preview}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 201
        ), f'Actual status code was {edit_addon.status_code}'
        # verify the image has been uploaded by checking the image location (should be '/user_media/')
        assert f'{base_url}/user-media/previews/' in edit_addon.json()['image_url']
        assert edit_addon.json()['position'] == count


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_previews_add_caption(base_url, session_auth):
    """Adds a short text for each screenshot uploaded for an addon"""
    addon = payloads.edit_addon_details['slug']
    # capture the preview ids to be used in the PATCH request and add them to a list
    previews_id = []
    get_addon = requests.get(
        url=f'{base_url}{_addon_create}{addon}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    r = get_addon.json()
    for image in r['previews']:
        previews_id.append(image.get('id'))
    payload = payloads.preview_captions
    # add a caption for all the available previews
    for preview in previews_id:
        edit_addon = requests.patch(
            url=f'{base_url}{_addon_create}{addon}/previews/{preview}/',
            headers={
                'Authorization': f'Session {session_auth}',
                'Content-Type': 'application/json',
            },
            data=json.dumps(payload),
        )
        response = edit_addon.json()
        assert (
            edit_addon.json()['caption'] == payload['caption']
        ), f'Actual response was {response}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_no_image_attached(base_url, session_auth):
    """Send a screenshot upload request without adding an image"""
    addon = payloads.edit_addon_details['slug']
    edit_addon = requests.post(
        url=f'{base_url}{_addon_create}{addon}/previews/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        edit_addon.status_code == 400
    ), f'Actual status code was {edit_addon.status_code}'
    assert (
        'No file was submitted.' in edit_addon.text
    ), f'Actual response message was {edit_addon.text}'


@pytest.mark.parametrize(
    'count, preview',
    enumerate(
        [
            'img/bmp_icon.bmp',
            'img/static_gif.gif',
            'img/animated_png.png',
            'img/invalid_image.png',
        ]
    ),
    ids=[
        'BMP screenshot',
        'GIF static screenshot',
        'PNG animated screenshot',
        'Non image file with a .png extension',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_add_invalid_image(base_url, session_auth, count, preview, variables):
    """Verify that requests fail if images do not meet these acceptance criteria:
    PNG or JPG, non-animated images, valid image file"""
    addon = payloads.edit_addon_details['slug']
    with open(preview, 'rb') as img:
        edit_addon = requests.post(
            url=f'{base_url}{_addon_create}{addon}/previews/',
            headers={'Authorization': f'Session {session_auth}'},
            files={'image': img},
        )
        print(
            f'For image "{preview}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f'Actual status code was {edit_addon.status_code}'
        # check that the validation messages expected for each image type are matching the API response
        assert variables['image_validation_messages'][count] in edit_addon.text


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_extension_delete_previews(base_url, session_auth):
    """Verify that addon previews can be deleted"""
    addon = payloads.edit_addon_details['slug']
    # get the preview ids for the available images
    preview_ids = []
    get_addon = requests.get(
        url=f'{base_url}{_addon_create}{addon}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    r = get_addon.json()
    for image in r['previews']:
        preview_ids.append(image.get('id'))
    for preview_id in preview_ids:
        delete_image = requests.delete(
            url=f'{base_url}{_addon_create}{addon}/previews/{preview_id}',
            headers={'Authorization': f'Session {session_auth}'},
        )
        assert (
            delete_image.status_code == 204
        ), f'Actual status code was {delete_image.status_code}'
    # get the add-on details again
    get_addon = requests.get(
        url=f'{base_url}{_addon_create}{addon}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    # check that there are no screenshots left for this addon
    assert len(get_addon.json()['previews']) == 0


@pytest.mark.serial
@pytest.mark.create_session('api_user')
@pytest.mark.clear_session
def test_delete_extension_valid_token(selenium, base_url, session_auth, variables):
    addon = payloads.edit_addon_details['slug']
    get_delete_confirm = requests.get(
        url=f'{base_url}{_addon_create}{addon}/delete_confirm/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    get_delete_confirm.raise_for_status()
    r = get_delete_confirm.json()
    token = r['delete_confirm']
    delete_addon = requests.delete(
        url=f'{base_url}{_addon_create}{addon}/',
        headers={'Authorization': f'Session {session_auth}'},
        params={'delete_confirm': token},
    )
    assert (
        delete_addon.status_code == 204
    ), f'Actual status code was {delete_addon.status_code}'
    get_addon = requests.get(
        url=f'{base_url}{_addon_create}{addon}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        get_addon.status_code == 404
    ), f'Actual status code was {get_addon.status_code}'
