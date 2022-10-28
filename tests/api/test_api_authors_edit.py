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
def test_addon_author_decline_invitation(base_url, session_auth, variables):
    """With a user that was invited to become an addon author, decline the invitation received"""
    addon = payloads.edit_addon_details['slug']
    decline_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/decline/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        decline_invite.status_code == 200
    ), f'Actual response: {decline_invite.status_code}, {decline_invite.text}'
    # try to re-decline invitation to make sure only once it's possible and there are no unexpected errors raised
    redecline_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/decline/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        redecline_invite.status_code == 403
    ), f'Actual response: {decline_invite.status_code}, {decline_invite.text}'
    # After having declined an invitation, try to confirm it; this should not be allowed
    confirm_declined_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/confirm/',
        headers={'Authorization': f'Session {session_auth}'},
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


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_list_pending_authors(base_url, session_auth, variables):
    """Check that users invited to become addon authors are listed in the pending authors queue"""
    addon = payloads.edit_addon_details['slug']
    # this is the author that should be pending for confirmation
    author = variables['api_post_valid_author']
    get_pending_authors = requests.get(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    get_pending_authors.raise_for_status()
    assert author == get_pending_authors.json()[0].get('user_id')


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_get_pending_author_details(base_url, session_auth, variables):
    """Check that the author details (role, position, visibility) set up in the request
    are returned in the pending author details API"""
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_valid_author']
    get_pending_author_details = requests.get(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/{author}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    get_pending_author_details.raise_for_status()
    pending_author = get_pending_author_details.json()
    # check that the author details match the actual author that is currently pending
    assert author == pending_author['user_id']
    assert payloads.author_stats['role'] == pending_author['role']
    assert payloads.author_stats['listed'] == pending_author['listed']


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_edit_pending_author(base_url, session_auth, variables):
    """As the user who initiated the author request, edit the details (role, visibility) of
    the invite and make sure that the changes are applied correctly"""
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_valid_author']
    payload = {'role': 'owner', 'listed': True}
    edit_pending_author_details = requests.patch(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/{author}/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    edit_pending_author_details.raise_for_status()
    pending_author = edit_pending_author_details.json()
    # check that the author details have been updated
    assert author == pending_author['user_id']
    assert payload['role'] == pending_author['role']
    assert payload['listed'] == pending_author['listed']


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_delete_pending_author(base_url, session_auth, variables):
    """As the user who initiated the author request, delete the invite before the
    new author had the chance to confirm it"""
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_valid_author']
    delete_pending_author = requests.delete(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/{author}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        delete_pending_author.status_code == 204
    ), f'Actual response: {delete_pending_author.status_code}, {delete_pending_author.text}'


@pytest.mark.serial
@pytest.mark.create_session('staff_user')
def test_addon_author_confirm_deleted_invitation(base_url, session_auth, variables):
    """With the author that was invited, try to accept the deleted invite to make sure it is not possible"""
    addon = payloads.edit_addon_details['slug']
    confirm_deleted_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/confirm/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        confirm_deleted_invite.status_code == 403
    ), f'Actual response: {confirm_deleted_invite.status_code}, {confirm_deleted_invite.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_invite_multiple_authors(base_url, session_auth, variables):
    """Check that an addon owner can invite multiple users to become addon authors
    in addition to the one added previously"""
    addon = payloads.edit_addon_details['slug']
    # invite the first author
    first_author = variables['api_post_valid_author']
    payload = {**payloads.author_stats, 'user_id': first_author, 'position': 1}
    second_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        second_invite.status_code == 201
    ), f'Actual response: {second_invite.status_code}, {second_invite.text}'
    # invite the second author
    second_author = variables['api_post_additional_author']
    payload = {**payloads.author_stats, 'user_id': second_author, 'position': 2}
    second_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        second_invite.status_code == 201
    ), f'Actual response: {second_invite.status_code}, {second_invite.text}'
    # verify that both users are present in the pending authors list
    get_pending_authors = requests.get(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert second_author == get_pending_authors.json()[0].get('user_id')
    assert first_author == get_pending_authors.json()[1].get('user_id')


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_invite_same_author_twice(base_url, session_auth, variables):
    """Check that an author can only be invited once, if the invitation is still active"""
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_additional_author']
    payload = {**payloads.author_stats, 'user_id': author, 'position': 2}
    duplicate_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        duplicate_invite.status_code == 400
    ), f'Actual response: {duplicate_invite.status_code}, {duplicate_invite.text}'
    assert (
        'An author can only be present once.' in duplicate_invite.text
    ), f'Actual response message was {duplicate_invite.text}'


@pytest.mark.serial
@pytest.mark.create_session('staff_user')
def test_addon_confirm_invitation_with_correct_user(base_url, session_auth, variables):
    addon = payloads.edit_addon_details['slug']
    accept_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/confirm/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        accept_invite.status_code == 200
    ), f'Actual response: {accept_invite.status_code}, {accept_invite.text}'
    # try to re-confirm invitation to make sure only once it's possible and there are no unexpected errors
    reconfirm_invite = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/confirm/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        reconfirm_invite.status_code == 403
    ), f'Actual response {reconfirm_invite.status_code}, {reconfirm_invite.text}'


@pytest.mark.serial
@pytest.mark.create_session('staff_user')
def test_addon_developer_role_cannot_add_authors(base_url, session_auth, variables):
    """Check that an author with a 'developer' role doesn't have the rights to invite other authors
    for an addon; only authors with 'owner' roles have the rights to invite other users"""
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_additional_author']
    payload = {**payloads.author_stats, 'user_id': author, 'position': 3}
    invite_author = requests.post(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        invite_author.status_code == 403
    ), f'Actual response: {invite_author.status_code}, {invite_author.text}'
    assert (
        'You do not have permission to perform this action.' in invite_author.text
    ), f'Actual message was {invite_author.text}'


@pytest.mark.serial
@pytest.mark.create_session('staff_user')
def test_addon_developer_role_cannot_edit_pending_author(
    base_url, session_auth, variables
):
    """Check that an author with a 'developer' role doesn't have the rights to edit details
    for other pending authors; only authors with 'owner' roles have the rights to make changes"""
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_additional_author']
    payload = {'role': 'owner', 'listed': True}
    edit_authors = requests.patch(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/{author}/',
        headers={
            'Authorization': f'Session {session_auth}',
            'Content-Type': 'application/json',
        },
        data=json.dumps(payload),
    )
    assert (
        edit_authors.status_code == 403
    ), f'Actual response: {edit_authors.status_code}, {edit_authors.text}'


@pytest.mark.serial
@pytest.mark.create_session('staff_user')
@pytest.mark.clear_session
def test_addon_developer_role_cannot_delete_pending_author(
    base_url, selenium, session_auth, variables
):
    """Check that an author with a 'developer' role doesn't have the rights to delete other
    pending authors; only authors with 'owner' roles have the rights to delete them"""
    addon = payloads.edit_addon_details['slug']
    author = variables['api_post_additional_author']
    delete_author = requests.delete(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/{author}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        delete_author.status_code == 403
    ), f'Actual response: {delete_author.status_code}, {delete_author.text}'


@pytest.mark.serial
@pytest.mark.create_session('api_user')
def test_addon_delete_all_active_and_pending_authors(base_url, session_auth, variables):
    """As the addon owner, delete all additional authors (pending or active)"""
    addon = payloads.edit_addon_details['slug']
    active_author = variables['api_post_valid_author']
    pending_author = variables['api_post_additional_author']
    # delete active author (invitation accepted)
    delete_active_author = requests.delete(
        url=f'{base_url}{_addon_create}{addon}/authors/{active_author}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        delete_active_author.status_code == 204
    ), f'Actual response: {delete_active_author.status_code}, {delete_active_author.text}'
    # delete the pending author (invitation not confirmed)
    delete_pending_author = requests.delete(
        url=f'{base_url}{_addon_create}{addon}/pending-authors/{pending_author}/',
        headers={'Authorization': f'Session {session_auth}'},
    )
    assert (
        delete_pending_author.status_code == 204
    ), f'Actual response: {delete_pending_author.status_code}, {delete_pending_author.text}'
