import time
import pytest
import requests

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.frontend.details import Detail
from pages.desktop.frontend.home import Home
from pages.desktop.frontend.login import Login
from pages.desktop.frontend.search import Search
from pages.desktop.frontend.static_pages import StaticPages
from pages.desktop.frontend.users import User


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.nondestructive
def test_login(selenium, base_url, wait):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login("regular_user")
    # the AMO header state changed after the transition from FxA so we have to
    # reassign it to another variable because 'page' can become stale at this point
    username = Home(selenium, base_url).wait_for_page_to_load()
    # verifies that the user display_name is visible after log in
    username.header.user_header_display_name("regular_user")


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.nondestructive
def test_logout(base_url, selenium):
    """User can logout"""
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login("regular_user")
    page.logout()

@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_menu_collections_link(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login("regular_user")
    # clicks on View My Collections in the user menu
    # and checks that the user collections page opens
    count = 0
    landing_page = ".CollectionList-info"
    page.header.click_user_menu_links(count, landing_page)


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_menu_view_profile(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login("regular_user")
    # clicks on View Profile in the user menu and checks that the correct page opens
    count = 1
    landing_page = ".UserProfile-name"
    page.header.click_user_menu_links(count, landing_page)


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_menu_edit_profile(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login("regular_user")
    # clicks on Edit Profile in the user menu and checks that the correct page opens
    count = 2
    landing_page = ".UserProfileEdit-displayName"
    page.header.click_user_menu_links(count, landing_page)

@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.nondestructive
def test_register_new_account(base_url, selenium, wait):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.register()
    # reassign AMO homepage it to another variable because 'page' can become stale at this point
    username = Home(selenium, base_url).wait_for_page_to_load()
    # check that a new user has been created (default user prefix should be 'Firefox user')
    username.header.user_header_display_name("Firefox user")

@pytest.mark.serial
@pytest.mark.nondestructive
@pytest.mark.login("developer")
def test_user_menu_click_user_menu_links(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    # Click Submit New Add-on
    count = 3
    landing_page = ".section header h2"
    page.header.click_user_menu_links(count, landing_page)
    Home(selenium, base_url).open().wait_for_page_to_load()
    # Click Submit New Theme
    count = 4
    landing_page = ".section header h2"
    page.header.click_user_menu_links(count, landing_page)
    Home(selenium, base_url).open().wait_for_page_to_load()
    # Click Manage Submissions
    count = 5
    landing_page = ".submission-type-tabs a:nth-child(1)"
    page.header.click_user_menu_links(count, landing_page)


@pytest.mark.serial
@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_user_developer_notifications(base_url, selenium, variables, wait):
    Home(selenium, base_url).open().wait_for_page_to_load()
    user = User(selenium, base_url).open().wait_for_page_to_load()
    # verifies that information messages about the scope of notifications are displayed
    assert variables["notifications_info_text"] in user.edit.notifications_info_text
    assert variables["notifications_help_text"] in user.edit.notifications_help_text
    # there are 8 types of notifications a developer will/can choose to receive
    wait.until(
        lambda _: len(user.edit.notification_text) == 8,
        message=f'Actual number of notifications displayed was "{len(user.edit.notification_text)}"',
    )
    count = 0
    while count < len(user.edit.notification_text):
        assert (
            variables["notifications"][count] in user.edit.notification_text[count].text
        )
        count += 1


@pytest.mark.serial
@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_user_mandatory_notifications(base_url, selenium):
    Home(selenium, base_url).open().wait_for_page_to_load()
    user = User(selenium, base_url).open().wait_for_page_to_load()
    # notifications 5 to 7 are mandatory for developers; clicking the checkboxes should have no effect
    for checkbox in user.edit.notifications_checkbox[4:7]:
        checkbox.click()
    user.edit.submit_changes()
    user.wait_for_user_to_load()
    user.view.click_edit_profile_button()
    # checks that the mandatory notification checkboxes are still selected
    for checkbox in user.edit.notifications_checkbox[4:7]:
        assert checkbox.is_selected()

@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.login("reusable_user")
def test_user_edit_profile(base_url, selenium, variables):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    # make sure that the submit changes button is disabled if display_name is not filled in
    assert user.edit.submit_changes_button_disabled.is_displayed()
    # fill in the Edit profile form fields
    user.edit.display_name(variables["display_name"])
    with pytest.raises(NoSuchElementException):
        user.edit.submit_changes_button_disabled.is_displayed()
    user.edit.homepage_link(variables["homepage"])
    user.edit.location(variables["location"])
    user.edit.occupation(variables["occupation"])
    user.edit.biography(variables["biography"])
    user.edit.upload_picture("profile_picture.png")
    # checks that the picture uploaded by the user is displayed
    user.edit.profile_picture_is_displayed()
    user.edit.submit_changes()
    # checks that the updated display name is visible in the header
    user.header.user_header_display_name(variables["display_name"])


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.create_session('reusable_user')
def test_user_view_profile(base_url, selenium, variables):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    # opens the View profile page
    user.edit.click_view_profile_link()
    # checks that the information provided in the user_edit_profile test
    # is present on the user View profile page
    assert user.view.user_profile_icon.is_displayed()
    assert variables["display_name"] in user.user_display_name.text
    assert variables["homepage"] in user.view.user_homepage
    assert variables["location"] in user.view.user_location
    assert variables["occupation"] in user.view.user_occupation
    assert variables["biography"] in user.view.user_biography
    # clicks on the Edit profile button and checks that the Edit profile page opens
    user.view.click_edit_profile_button()
    user.wait_for_current_url("/users/edit")


@pytest.mark.serial
@pytest.mark.create_session('reusable_user')
def test_user_change_profile_picture(base_url, selenium, wait):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    # opens the View profile page
    user.edit.click_view_profile_link()
    # stores the source of the old profile picture in View profile
    view_old_icon = user.view.icon_source
    user.view.click_edit_profile_button()
    # stores the source of the old profile picture in Edit profile
    edit_old_icon = user.edit.picture_source
    user.edit.upload_picture("profile_picture_alt.png")
    # waits for the image source to change after the new image is uploaded and verifies
    # that the new source doesn't match the old source, i.e. image has changed
    wait.until(
        lambda _: edit_old_icon != user.edit.picture_source,
        message=f"old icon = {edit_old_icon}, new icon = {user.edit.picture_source}",
    )
    user.edit.submit_changes()
    # reassign 'User' to a new variable since the page has been refreshed and 'user' can become stale
    view_profile = User(selenium, base_url).wait_for_user_to_load()
    # checks that the image change is also reflected in the view profile page
    wait.until(
        lambda _: view_old_icon != view_profile.view.icon_source,
        message="The profile icon change was not properly recorded",
    )


@pytest.mark.serial
@pytest.mark.create_session('reusable_user')
def test_user_delete_profile_picture(base_url, selenium):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.edit.delete_profile_picture()
    # cancel and then click on delete picture again
    user.edit.cancel_delete_picture()
    user.edit.delete_profile_picture()
    user.edit.confirm_delete_picture()
    assert "Picture successfully deleted" in user.edit.picture_delete_success_message
    # checks that the default profile avatar is present after the picture is deleted
    assert user.edit.profile_avatar_placeholder.is_displayed()
    user.edit.click_view_profile_link()
    # checks that the picture is deleted in the View profile page as well
    assert user.view.user_profile_icon_placeholder.is_displayed()


@pytest.mark.serial
@pytest.mark.create_session('reusable_user')
def test_user_update_profile(base_url, selenium, variables):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    updated_name = "new_display_name"
    # update field
    user.edit.display_name_field.clear()
    user.edit.display_name_field.send_keys(updated_name)
    # clear field
    user.edit.location_field.clear()
    # append to field text
    user.edit.biography(variables["biography_extra"])
    user.edit.submit_changes()
    user.wait_for_user_to_load()
    assert updated_name in user.user_display_name.text
    # check that location field is not displayed
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, ".UserProfile-location")
    biography_text = variables["biography"] + variables["biography_extra"]
    assert biography_text in user.view.user_biography


@pytest.mark.serial
@pytest.mark.create_session('reusable_user')
def test_user_update_url(base_url, selenium, variables):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    initial_page_url = selenium.current_url
    # test not a URL, this should not pass the client validation
    # it should not submit, red error message should not be displayed
    user.edit.homepage_link_field.clear()
    user.edit.homepage_link_field.send_keys("invalid.com")
    user.edit.update_profile()
    assert initial_page_url in selenium.current_url
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, ".Notice-error .Notice-text")

    # test invalid URL, this should not pass the API validation
    # it should not submit, red error message should be displayed
    user.edit.homepage_link_field.clear()
    user.edit.homepage_link_field.send_keys("https://invalid,com")
    user.edit.update_profile()
    user.wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                ".Notice-error .Notice-text",
            )
        )
    )
    assert initial_page_url in selenium.current_url
    assert variables["invalid_url_error"] in user.edit.invalid_url_error_text


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.create_session('reusable_user')
def test_user_delete_profile(base_url, selenium):
    user = User(selenium, base_url).open().wait_for_page_to_load()
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
@pytest.mark.login("reusable_user")
def test_user_account_manage_section(base_url, selenium, variables):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    email = Login(selenium, base_url)
    # verifies if the correct email is displayed in the email field
    assert email.REUSABLE_USER_EMAIL in user.edit.email_field
    # checks that the email filed shows a help text and a link to a sumo page
    assert variables["email_field_help_text"] in user.edit.email_field_help_text
    user.edit.email_field_help_link()
    selenium.back()
    user.wait_for_page_to_load()
    # verifies that the Manage account link opens the FxA account page
    user.edit.link_to_fxa_account()


@pytest.mark.serial
@pytest.mark.create_session("reusable_user")
def test_user_data_for_deleted_profile(base_url, selenium):
    """When a profile is deleted from AMO, the user data is deleted.
    However, the FxA account for that user still exists, so they can log into AMO
    with the same email and a new entry in the database is created for them"""
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.edit.click_view_profile_link()
    # checks that the default icon and display name are present for the deleted user
    assert user.view.user_profile_icon_placeholder.is_displayed
    assert "Firefox user" in user.user_display_name.text


@pytest.mark.serial
@pytest.mark.nondestructive
@pytest.mark.create_session('reusable_user')
@pytest.mark.clear_session
def test_user_regular_has_no_role(base_url, selenium):
    Home(selenium, base_url).open().wait_for_page_to_load()
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.edit.click_view_profile_link()
    # check that we do not display role badges for regular users
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, ".UserProfile-developer")
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, ".UserProfile-artist")


@pytest.mark.serial
def test_user_regular_notifications(base_url, selenium, variables):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    user.login("reusable_user")
    # regular users can only opt in/out for 2 notifications
    assert len(user.edit.notification_text) == 2
    count = 0
    while count < len(user.edit.notification_text):
        assert (
            variables["notifications"][count] in user.edit.notification_text[count].text
        )
        count += 1


@pytest.mark.serial
@pytest.mark.nondestructive
@pytest.mark.skip(
    reason="Intermittent issue, see https://github.com/mozilla/addons-server/issues/20965"
)
def test_user_notifications_subscriptions(base_url, selenium, wait):
    edit_user = User(selenium, base_url).open().wait_for_page_to_load()
    edit_user.login("staff_user")
    # verify that the first 7 notifications are selected by default
    for checkbox in edit_user.edit.notifications_checkbox[0:7]:
        assert checkbox.is_selected()
    # unsubscribe from one of the non-mandatory notifications
    edit_user.edit.notifications_checkbox[0].click()
    time.sleep(2)
    edit_user.edit.submit_changes()
    time.sleep(3)
    User(selenium, base_url).open().wait_for_page_to_load()
    # verify that the notification checkbox is no longer selected
    with pytest.raises(AssertionError):
        assert edit_user.edit.notifications_checkbox[0].is_selected()
    # subscribe to the notification again
    edit_user.edit.notifications_checkbox[0].click()
    edit_user.edit.submit_changes()
    time.sleep(2)
    User(selenium, base_url).open().wait_for_page_to_load()
    assert edit_user.edit.notifications_checkbox[0].is_selected()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_developer_role(base_url, selenium, variables):
    developer = variables["developer_profile"]
    selenium.get(f"{base_url}/user/{developer}")
    user = User(selenium, base_url).wait_for_user_to_load()
    # check that the 'developer' role badge is displayed in the view profile page
    assert "Add-ons developer" in user.view.developer_role.text
    assert user.view.developer_role_icon.is_displayed()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_theme_artist_role(base_url, selenium, variables):
    artist = variables["theme_artist_profile"]
    selenium.get(f"{base_url}/user/{artist}")
    user = User(selenium, base_url).wait_for_user_to_load()
    # check that the 'artist' role badge is displayed in the view profile page
    assert "Theme artist" in user.view.artist_role.text
    assert user.view.artist_role_icon.is_displayed()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_artist_and_developer_role(base_url, selenium, variables):
    dev_artist = variables["developer_and_artist_role"]
    selenium.get(f"{base_url}/user/{dev_artist}")
    user = User(selenium, base_url).wait_for_user_to_load()
    # check that a user who is both a developer and a theme artist has both role badges
    assert "Add-ons developer" in user.view.developer_role.text
    assert user.view.developer_role_icon.is_displayed()
    assert "Theme artist" in user.view.artist_role.text
    assert user.view.artist_role_icon.is_displayed()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_non_developer_user_profile_is_not_public(base_url, selenium, variables):
    """Non developer users' profile pages are not publicly available;
    when accessed, they will return a 404 page"""
    non_developer_user = variables["non_developer_user"]
    selenium.get(f"{base_url}/user/{non_developer_user}")
    page = StaticPages(selenium, base_url).wait_for_page_to_load()
    assert variables["not_found_page_title"] in page.page_header
    response = requests.head(selenium.current_url)
    assert (
        response.status_code == 404
    ), f"The response status code was {response.status_code}"


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_addon_cards_for_users_with_multiple_roles(base_url, selenium, variables):
    """Users who are both extension developers and theme artists should have the Extensions
    and Themes cards displayed on their profiles. Additionally, the User reviews card should
    be hidden when the profile is viewed by another user"""
    user_profile = variables["developer_and_artist_role"]
    selenium.get(f"{base_url}/user/{user_profile}")
    user = User(selenium, base_url)
    user_profile_name = user.user_display_name.text
    # check that extensions results have the following properties displayed:
    assert f"Extensions by {user_profile_name}" in user.view.user_extensions_card_header
    for extension in user.view.user_extensions_results:
        assert extension.search_name.is_displayed()
        assert extension.search_result_icon.is_displayed()
        assert extension.search_result_rating_stars.is_displayed()
        assert user_profile_name in extension.search_result_author.text
        assert extension.search_result_users.is_displayed()
        assert extension.search_result_summary.is_displayed()
    # check that themes results have the following properties displayed:
    assert f"Themes by {user_profile_name}" in user.view.user_themes_card_header
    for theme in user.view.user_themes_results:
        assert theme.search_name.is_displayed()
        assert theme.search_result_icon.is_displayed()
        assert theme.search_result_users.is_displayed()
    # verify that the user profile ratings card is not displayed when viewed by another user
    with pytest.raises(
        Exception,
        match="Message: Unable to locate element: .UserProfile-reviews",
    ):
        selenium.find_element(By.CLASS_NAME, "UserProfile-reviews")


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_profile_extensions_card(base_url, selenium, variables):
    page = variables["developer_and_artist_role"]
    selenium.get(f"{base_url}/user/{page}")
    user = User(selenium, base_url).wait_for_user_to_load()
    extensions = user.view.user_extensions_results
    # the extensions card can display up to 10 extensions per page with a minimum of 1
    assert len(extensions) in range(
        1, 11
    ), f"The list contains {len(extensions)} extensions"
    # checks that pagination is present if the user has more than 10 extensions
    try:
        user.view.extensions_pagination.is_displayed()  # if not present, exception is raised
        first_page_list = [el.name for el in user.view.user_extensions_results]
        user.view.extensions_next_page()
        assert (
            "2" in user.view.extensions_page_number
        ), f"Pagination was:{user.view.extensions_page_number}"
        # verifies that extensions search results have changed
        assert first_page_list != [el.name for el in user.view.user_extensions_results]
    except NoSuchElementException as exception:
        # making sure that we only ignore the exception for the 'extensions_pagination' element
        if ".AddonsCard--vertical .Paginate" in exception.msg:
            print(
                f"The user had {len(extensions)} extensions, so pagination is not present"
            )
        else:
            pytest.fail(exception.msg)


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_profile_themes_card(base_url, selenium, variables):
    page = variables["developer_and_artist_role"]
    selenium.get(f"{base_url}/user/{page}")
    user = User(selenium, base_url).wait_for_user_to_load()
    themes = user.view.user_themes
    # the themes card can display up to 12 themes per page with a minimum of 1
    themes_count = len(themes.result_list.themes)
    assert themes_count in range(1, 13), f"The list contains {themes_count} extensions"
    # checks that pagination is present if the user has more than 12 themes
    try:
        user.view.themes_pagination.is_displayed()  # if not present, exception is raised
        first_page_list = [el.name for el in themes.result_list.themes]
        user.view.themes_next_page()
        assert (
            "2" in user.view.themes_page_number
        ), f"Pagination was:{user.view.themes_page_number}"
        # verifies that themes search results have changed
        assert first_page_list != [el.name for el in themes.result_list.themes]
    except NoSuchElementException as exception:
        # making sure that we only ignore the exception for the 'themes_pagination' element
        if ".AddonsByAuthorsCard--theme .Paginate" in exception.msg:
            print(f"The user had {themes_count} themes, so pagination is not present")
        else:
            pytest.fail(exception.msg)


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_profile_open_extension_detail_page(base_url, selenium, variables):
    page = variables["developer_profile"]
    selenium.get(f"{base_url}/user/{page}")
    extension = Search(selenium, base_url).wait_for_page_to_load()
    extension_name = extension.result_list.search_results[0].name
    # clicks on an extension in the user profile page
    detail_extension = extension.result_list.click_search_result(0)
    # checks that the expected extension detail page is opened
    assert extension_name in detail_extension.name


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_profile_open_theme_detail_page(base_url, selenium, variables):
    artist = variables["theme_artist_profile"]
    selenium.get(f"{base_url}/user/{artist}")
    theme = Search(selenium, base_url).wait_for_page_to_load()
    theme_name = theme.result_list.themes[0].name
    # clicks on a theme in the user profile page
    theme_detail = theme.result_list.click_search_result(0)
    # checks that the expected theme detail page is opened
    assert theme_name in theme_detail.name


@pytest.mark.serial
@pytest.mark.nondestructive
@pytest.mark.login("submissions_user")
def test_user_profile_write_review(base_url, selenium, variables, wait):
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # addon.login('submissions_user')
    # post a rating on the detail page
    addon.ratings.rating_stars[4].click()
    # navigate to the user profile page to write a review
    count = 1
    landing_page = ".UserProfile-name"
    addon.header.click_user_menu_links(count, landing_page)
    user = User(selenium, base_url).wait_for_user_to_load()
    # the review card doesn't have preload elements, so we need to wait for it to load individually
    user.view.user_reviews_section_loaded()
    addon.ratings.write_a_review.click()
    review_text = variables["initial_text_input"]
    addon.ratings.review_text_input(review_text)
    addon.ratings.submit_review()
    # verifies that the written review is displayed
    wait.until(
        lambda _: user.view.user_review_items[0].review_body == review_text,
        message=f'Expected text "{review_text}" not in "{user.view.user_review_items[0].review_body}"',
    )


@pytest.mark.serial
@pytest.mark.nondestructive
@pytest.mark.create_session("submissions_user")
def test_user_profile_edit_review(base_url, selenium, variables, wait):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    # user.login('submissions_user')
    user.edit.click_view_profile_link()
    # the review card doesn't have preload elements, so we need to wait for it to load individually
    user.view.user_reviews_section_loaded()
    edit = Detail(selenium, base_url)
    edit.ratings.edit_review.click()
    edited_review_text = variables["edited_text_input"]
    edit.ratings.clear_review_text_field()
    edit.ratings.review_text_input(edited_review_text)
    edit.ratings.submit_review()
    # verifies that the review text has been updated
    wait.until(
        lambda _: edited_review_text in user.view.user_review_items[0].review_body,
        message=f'Expected text "{edited_review_text}" not in "{user.view.user_review_items[0].review_body}"',
    )


@pytest.mark.serial
@pytest.mark.nondestructive
@pytest.mark.create_session("submissions_user")
def test_user_profile_delete_review(base_url, selenium, variables, wait):
    user = User(selenium, base_url).open().wait_for_page_to_load()
    # user.login('submissions_user')
    user.edit.click_view_profile_link()
    # the review card doesn't have preload elements, so we need to wait for it to load individually
    user.view.user_reviews_section_loaded()
    review_list_count = len(user.view.user_review_items)
    delete = Detail(selenium, base_url)
    delete.ratings.delete_review.click()
    user.view.user_review_items[0].click_confirm_delete_button()
    # confirms that the review was deleted from the list
    wait.until(
        lambda _: len(user.view.user_review_items) == review_list_count - 1,
        message=f"Expected {review_list_count - 1} reviews but got {len(user.view.user_review_items)}",
    )


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_abuse_report(base_url, selenium, variables, wait):
    developer = variables["developer_profile"]
    selenium.get(f"{base_url}/user/{developer}")
    user = User(selenium, base_url).wait_for_user_to_load()
    user.view.click_user_abuse_report()
    # checks the information present in the abuse report form before submission
    assert (
        variables["user_abuse_initial_form_header"]
        in user.view.abuse_report_form_header
    )
    assert (
        variables["user_abuse_form_initial_help_text"]
        in user.view.abuse_report_form_help_text
    )
    assert (
        variables["user_abuse_form_additional_help_text"]
        in user.view.abuse_report_form_additional_help_text
    )
    # click on Cancel to close the form
    user.view.cancel_abuse_report_form()
    user.view.click_user_abuse_report()
    # checks that the submit button is disabled if no text is inserted
    assert user.view.abuse_report_submit_disabled.is_displayed()
    user.view.user_abuse_report_input_text(variables["user_abuse_input_text"])
    user.view.submit_user_abuse_report()
    # verifies the abuse report form after submission
    wait.until(
        lambda _: variables["user_abuse_confirmed_form_header"]
        in user.view.abuse_report_form_header,
        message=f'Abuse report form header was "{user.view.abuse_report_form_header}"',
    )
    assert (
        variables["user_abuse_form_confirmed_help_text"]
        in user.view.user_abuse_confirmation_message
    )
