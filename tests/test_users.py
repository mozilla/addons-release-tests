import pytest

from selenium.webdriver.support.wait import WebDriverWait

from pages.desktop.home import Home
from pages.desktop.login import Login
from pages.desktop.users import User
from scripts import custom_waits


@pytest.mark.nondestructive
def test_login(selenium, base_url):
    page = Home(selenium, base_url).open()
    user = 'regular_user'
    page.login(user)
    page.header.user_header_display_name(user)


@pytest.mark.nondestructive
def test_logout(base_url, selenium):
    """User can logout"""
    page = Home(selenium, base_url).open()
    user = 'regular_user'
    page.login(user)
    page.logout()
    assert not page.logged_in


@pytest.mark.nondestructive
def test_user_menu_collections_link(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login('regular_user')
    # clicks on View My Collections in the user menu
    # and checks that the user collections page opens
    count = 0
    landing_page = '.CollectionList-info'
    page.header.click_user_menu_links(count, landing_page)


@pytest.mark.nondestructive
def test_user_menu_view_profile(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login('regular_user')
    # clicks on View Profile in the user menu and checks that the correct page opens
    count = 1
    landing_page = '.UserProfile-name'
    page.header.click_user_menu_links(count, landing_page)


@pytest.mark.nondestructive
def test_user_menu_edit_profile(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login('regular_user')
    # clicks on Edit Profile in the user menu and checks that the correct page opens
    count = 2
    landing_page = '.UserProfileEdit-displayName'
    page.header.click_user_menu_links(count, landing_page)


@pytest.mark.nondestructive
def test_user_menu_devhub_links(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login('developer')
    count = 3
    landing_page = '.site-title.prominent'
    # there are 3 links pointing to DevHub pages in the user menu;
    # clicking through each of those links and checking that the correct page opens
    while count < 6:
        page.header.click_user_menu_links(count, landing_page)
        # returning to the homepage to select the next link
        selenium.back()
        # waiting for the homepage o reload
        page.wait_for_page_to_load()
        count += 1


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_edit_profile(base_url, selenium, variables):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.login('reusable_user')
    # fill in the Edit profile form fields
    user.edit.display_name(variables['display_name'])
    user.edit.homepage_link(variables['homepage'])
    user.edit.location(variables['location'])
    user.edit.occupation(variables['occupation'])
    user.edit.biography(variables['biography'])
    user.edit.upload_picture('profile_picture.png')
    # checks that the picture uploaded by the user is displayed
    user.edit.profile_picture_is_displayed()
    user.edit.submit_changes()
    # checks that the updated display name is visible in the header
    user.header.user_header_display_name(variables['display_name'])


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_view_profile(base_url, selenium, variables):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.login('reusable_user')
    # opens the View profile page
    user.edit.click_view_profile_link()
    # checks that the information provided in the user_edit_profile test
    # is present on the user View profile page
    assert user.view.user_profile_icon.is_displayed()
    assert variables['display_name'] in user.user_display_name
    assert variables['homepage'] in user.view.user_homepage
    assert variables['location'] in user.view.user_location
    assert variables['occupation'] in user.view.user_occupation
    assert variables['biography'] in user.view.user_biography
    # clicks on the Edit profile button and checks that the Edit profile page opens
    user.view.click_edit_profile_button()
    user.wait_for_current_url('/users/edit')


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_account_manage_section(base_url, selenium, variables):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.login('reusable_user')
    email = Login(selenium, base_url)
    # verifies if the correct email is displayed in the email field
    assert email.REUSABLE_USER_EMAIL in user.edit.email_field
    # checks that the email filed shows a help text and a link to a sumo page
    assert variables['email_field_help_text'] in user.edit.email_field_help_text
    user.edit.email_field_help_link()
    selenium.back()
    user.wait_for_page_to_load()
    # verifies that the Manage account link opens the FxA account page
    user.edit.link_to_fxa_account()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_change_profile_picture(base_url, selenium):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.login('reusable_user')
    # opens the View profile page
    user.edit.click_view_profile_link()
    # stores the source of the old profile picture in View profile
    view_old_icon = user.view.icon_source
    user.view.click_edit_profile_button()
    # stores the source of the old profile picture in Edit profile
    edit_old_icon = user.edit.picture_source
    user.edit.upload_picture('profile_picture_alt.png')
    # waits for the image source to change after the new image is uploaded and verifies
    # that the new source doesn't match the old source, i.e. image has changed
    WebDriverWait(selenium, 10).until(
        custom_waits.check_value_inequality(edit_old_icon, user.edit.picture_source)
    )
    user.edit.submit_changes()
    user.wait_for_user_to_load()
    # checks that the image change is also reflected in the view profile page
    assert view_old_icon != user.view.icon_source


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_delete_profile_picture(base_url, selenium):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.login('reusable_user')
    user.edit.delete_profile_picture()
    # cancel and then click on delete picture again
    user.edit.cancel_delete_picture()
    user.edit.delete_profile_picture()
    user.edit.confirm_delete_picture()
    assert 'Picture successfully deleted' in user.edit.picture_delete_success_message
    # checks that the default profile avatar is present after the picture is deleted
    assert user.edit.profile_avatar_placeholder.is_displayed()
    user.edit.click_view_profile_link()
    # checks that the picture is deleted in the View profile page as well
    assert user.view.user_profile_icon_placeholder.is_displayed()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_delete_profile(base_url, selenium):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.login('reusable_user')
    user.edit.delete_account()
    # click cancel to close the delete profile overlay
    user.edit.cancel_delete_account()
    # click on delete account again and this time confirm
    user.edit.delete_account()
    home = user.edit.confirm_delete_account()
    # checks that user is redirected to Homepage after account deletion
    assert home.primary_hero.is_displayed()
    # check that the user was logged out
    assert user.header.login_button.is_displayed()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_data_for_deleted_profile(base_url, selenium):
    """When a profile is deleted from AMO, the user data is deleted.
    However, the FxA account for that user still exists, so they can log into AMO
    with the same email and a new entry in the database is created for them"""
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.login('reusable_user')
    user.edit.click_view_profile_link()
    # checks that the default icon and display name are present for the deleted user
    assert user.view.user_profile_icon_placeholder.is_displayed
    assert 'Firefox user' in user.user_display_name
