import json
import requests
import pytest

from api import payloads

# endpoints used in the version edit tests
_addon_create = '/api/v5/addons/addon/'

# API endpoints covered are:
# add new author: https://addons-server.readthedocs.io/en/latest/topics/api/authors.html#pending-author-create
# confirm an invitation: https://addons-server.readthedocs.io/en/latest/topics/api/authors.html#pending-author-confirm
# decline an invitation: https://addons-server.readthedocs.io/en/latest/topics/api/authors.html#pending-author-decline
# list pending authors: https://addons-server.readthedocs.io/en/latest/topics/api/authors.html#pending-author-list
# edit pending authors: https://addons-server.readthedocs.io/en/latest/topics/api/authors.html#pending-author-edit
# delete pending authors: https://addons-server.readthedocs.io/en/latest/topics/api/authors.html#pending-author-delete
# edit existing authors: https://addons-server.readthedocs.io/en/latest/topics/api/authors.html#author-edit
# delete existing authors: https://addons-server.readthedocs.io/en/latest/topics/api/authors.html#author-delete


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_add_new_author(base_url, session_auth, variables):
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_valid_author']
    # create the payload with the fields required for a new author set-up
    payload = {**payloads.author_stats, 'user_id': author, 'position': 1}
    add_author = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        add_author.status_code == 201
    ), f'Actual response: {add_author.status_code}, {add_author.text}'
    # verify that the author ID added is returned in the API response 'user_id'
    assert author == add_author.json()['user_id']


@pytest.mark.serial
@pytest.mark.create_session('staff_user')
@pytest.mark.clear_session
def test_addon_author_decline_invitation(selenium, base_url, variables):
    """With a user that was invited to become an addon author, decline the invitation received"""
    session_auth = selenium.get_cookie('sessionid')
    addon = payloads.edit_addon_details['slug']
    decline_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/decline/',
        headers={'Authorization': f'Session {session_auth["value"]}'},
    )
    assert (
        decline_invite.status_code == 200
    ), f'Actual response: {decline_invite.status_code}, {decline_invite.text}'
    # try to re-decline invitation to make sure only once it's possible and there are no unexpected errors raised
    redecline_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/decline/',
        headers={'Authorization': f'Session {session_auth["value"]}'},
    )
    assert (
        redecline_invite.status_code == 403
    ), f'Actual response: {decline_invite.status_code}, {decline_invite.text}'
    # After having declined an invitation, try to confirm it; this should not be allowed
    confirm_declined_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/confirm/',
        headers={'Authorization': f'Session {session_auth["value"]}'},
    )
    assert (
        confirm_declined_invite.status_code == 403
    ), f'Actual response: {decline_invite.status_code}, {decline_invite.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_add_author_without_display_name(base_url, session_auth, variables):
    """It is mandatory for a user to have a display name set in order to be accepted as an addon author"""
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_author_no_display_name']
    payload = {'user_id': author, 'position': 2}
    add_author = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        add_author.status_code == 400
    ), f'Actual response: {add_author.status_code}, {add_author.text}'
    assert (
        'The account needs a display name before it can be added as an author.'
        in add_author.text
    ), f'Actual message was {add_author.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_add_restricted_author(base_url, session_auth, variables):
    """If a user is added to the email restriction list, it is not possible to add it as an addon author"""
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_author_no_dev_agreement']
    payload = {'user_id': author, 'position': 2}
    add_author = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        add_author.status_code == 400
    ), f'Actual response {add_author.status_code}, {add_author.text}'
    assert (
        'The email address used for your account is not allowed for add-on submission.'
        in add_author.text
    ), f'Actual message was {add_author.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_add_invalid_authors(base_url, session_auth, variables):
    """Try to add a non exiting user as an addon author"""
    addon = payloads.edit_addon_details['slug']
    payload = {**payloads.author_stats, 'user_id': 9999999999, 'position': 2}
    add_author = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        add_author.status_code == 400
    ), f'Actual response {add_author.status_code}, {add_author.text}'
    assert (
        'Account not found.' in add_author.text
    ), f'Actual response message was {add_author.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_confirm_invitation_with_wrong_user(base_url, session_auth, variables):
    """Send an author invitation to a user and try to confirm the invite with a different user"""
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_valid_author']
    payload = {**payloads.author_stats, 'user_id': author, 'position': 1}
    add_author = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        add_author.status_code == 201
    ), f'Actual response {add_author.status_code}, {add_author.text}'
    # confirm invitation with a user different from the one invited
    confirm_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/confirm/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        confirm_invite.status_code == 403
    ), f'Actual response: {confirm_invite.status_code}, {confirm_invite.text}'
