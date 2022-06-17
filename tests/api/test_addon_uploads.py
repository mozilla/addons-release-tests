import json
import time

import pytest
import requests

from api import payloads, api_helpers
from pages.desktop.frontend.home import Home

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
