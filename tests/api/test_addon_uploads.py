import json
import time

import pytest
import requests

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


@pytest.mark.login('api_user')
@pytest.mark.serial
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
@pytest.mark.clear_session
def test_upload_unlisted_extension(base_url, selenium, session_auth):
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
