import pytest

from pages.desktop.developers.devhub_home import DevHubHome
from scripts import reusables


@pytest.mark.sanity
@pytest.mark.serial
# The first test starts the browser with a normal login in order to store de session cookie
@pytest.mark.login('submissions_user')
def test_submit_unlisted_addon(selenium, base_url, variables, wait):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    submit_addon = page.click_submit_addon_button()
    # start the upload for an unlisted addon
    submit_addon.select_unlisted_option()
    submit_addon.click_continue()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_addon.firefox_compat_checkbox.is_selected())
    # select an addon to upload
    submit_addon.upload_addon('unlisted-addon.zip')
    submit_addon.is_validation_successful()
    assert submit_addon.success_validation_message.is_displayed()
    # on submit source code page, select 'No' as we do not test source code upload here
    source = submit_addon.click_continue_upload_button()
    source.select_no_to_omit_source()
    confirmation_page = source.continue_unlisted_submission()
    assert (
        variables['unlisted_submission_confirmation']
        in confirmation_page.submission_confirmation_messages[0].text
    )
    manage_addons = confirmation_page.click_manage_listing_button()
    manage_addons.sort_by_created()
    # checking that the latest add-on created is the one just submitted
    wait.until(lambda _: 'Unlisted-addon-auto' in manage_addons.addon_list[0].name)


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
def test_verify_if_version_is_autoapproved(selenium, base_url, variables, wait):
    """This test will wait (for max 5 minutes) until the status of an add-on changes to approved"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    my_addons = page.click_my_addons_header_link()
    # open the edit page of the latest listed add-on submitted
    edit_addon = my_addons.addon_list[0].click_addon_name()
    version_status = edit_addon.click_manage_versions_link()
    version_status.wait_for_version_autoapproval('Approved')


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
def test_submit_listed_addon(selenium, base_url, variables, wait):
    """Test covering the process of uploading a listed addon"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    submit_addon = page.click_submit_addon_button()
    # start the upload for a listed addon
    submit_addon.select_listed_option()
    submit_addon.click_continue()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_addon.firefox_compat_checkbox.is_selected())
    # select the Android compatibility checkbox
    submit_addon.android_compat_checkbox.click()
    submit_addon.upload_addon('listed-addon.zip')
    # waits for the validation to complete and checks that is successful
    submit_addon.is_validation_successful()
    # on submit source code page, select 'Yes' to upload source code
    source = submit_addon.click_continue_upload_button()
    source.select_yes_to_submit_source()
    source.choose_source('listed-addon.zip')
    details_form = source.continue_listed_submission()
    # setting a unique add-on name
    details_form.addon_name_field.clear()
    addon_name = f'Listed-{reusables.current_date()}-{reusables.get_random_string(5)}'
    details_form.set_addon_name(addon_name)
    details_form.set_addon_summary(variables['listed_addon_summary_en'])
    details_form.set_addon_description(variables['listed_addon_description_en'])
    # marks an add-on as experimental
    details_form.is_experimental.click()
    # flag add-on for payment requirements
    details_form.requires_payment.click()
    # reusables.scroll_into_view(selenium, details_form.categories_section)
    # set Firefox and Android categories for the addon
    details_form.select_firefox_categories(0)
    details_form.select_android_categories(0)
    details_form.email_input_field('some-mail@mail.com')
    details_form.support_site_input_field('https://example.com')
    # set an addon license from the available list
    details_form.select_license_options[0].click()
    details_form.set_privacy_policy(variables['listed_addon_privacy_policy_en'])
    details_form.set_reviewer_notes(variables['listed_addon_reviewer_notes'])
    # submit the add-on details
    confirmation_page = details_form.submit_addon()
    assert (
        variables['listed_submission_confirmation']
        in confirmation_page.submission_confirmation_messages[0].text
    )
    # go to the addon edit listing page and check that it was created
    edit_listing = confirmation_page.click_edit_listing_button()
    assert addon_name in edit_listing.name


@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
def test_addon_last_modified_date(selenium, base_url):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # check the last modified date in the latest submitted addon on Devhub homepage (should be current date)
    print(page.my_addons_list[0].my_addon_modified_date_text)
    assert (
        reusables.current_date() == page.my_addons_list[0].my_addon_modified_date_text
    )
    edit_addon = page.my_addons_list[0].click_my_addon_edit_link()
    # check the last modified date on the Edit listing page
    assert reusables.current_date() == edit_addon.last_modified_date


@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
def test_submit_mixed_addon_versions(selenium, base_url, variables, wait):
    """Uploads an unlisted version to an exiting listed addon"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    my_addons = page.click_my_addons_header_link()
    # open the edit page of the latest listed add-on submitted
    edit_addon = my_addons.addon_list[0].click_addon_name()
    submit_version = edit_addon.click_upload_version_link()
    submit_version.change_version_distribution()
    # select unlisted option for the new version
    submit_version.select_unlisted_option()
    submit_version.click_continue()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_version.firefox_compat_checkbox.is_selected())
    submit_version.upload_addon('mixed-addon-versions.zip')
    # wait for the validation to finish and check if it is successful
    submit_version.is_validation_successful()
    assert submit_version.success_validation_message.is_displayed()
    # on submit source code page, select No as we do not test source code upload here
    source = submit_version.click_continue_upload_button()
    source.select_no_to_omit_source()
    confirmation_page = source.continue_unlisted_submission()
    assert (
        variables['unlisted_submission_confirmation']
        in confirmation_page.submission_confirmation_messages[0].text
    )
    manage_addons = confirmation_page.click_manage_listing_button()
    edit_addon = manage_addons.addon_list[0].click_addon_name()
    # verify that the unlisted addon badge is now visible on the edit details page
    assert edit_addon.unlisted_version_tooltip.is_displayed()


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
def test_submit_listed_wizard_theme(selenium, base_url, variables, wait, delete_themes):
    """A test that checks a straight-forward theme submission with the devhub wizard"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    submit_addon = page.click_submit_theme_button()
    # start the upload for a listed theme
    submit_addon.select_listed_option()
    submit_addon.click_continue()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_addon.firefox_compat_checkbox.is_selected())
    create_theme = submit_addon.click_create_theme_button()
    theme_name = f'wizard_theme_{reusables.get_random_string(5)}'
    create_theme.set_theme_name(theme_name)
    create_theme.upload_theme_header('theme_header.png')
    wait.until(lambda _: create_theme.uploaded_image_preview.is_displayed())
    # make a note of the image source uploaded as the theme header
    uploaded_img_source = create_theme.uploaded_image_source
    # verify that the uploaded image is applied in the browser preview
    assert uploaded_img_source == create_theme.browser_preview_image
    theme_details = create_theme.submit_theme()
    # check that the name set earlier carried over
    assert theme_name in theme_details.addon_name_field.get_attribute('value')
    theme_details.set_addon_summary('Theme summary')
    # select a category for the theme
    theme_details.select_theme_categories(0)
    # set up a license for the theme based on 'Yes'[0]/'No'[1] options
    theme_details.select_theme_licence_sharing_rights(1)
    theme_details.select_theme_license_commercial_use(1)
    theme_details.select_theme_license_creation_rights(1)
    # check that the resulted license is 'All Rights Reserved'
    assert 'All Rights Reserved' in theme_details.generated_theme_license.text
    confirmation_page = theme_details.submit_addon()
    # verify that the theme preview has been generated after submission
    wait.until(lambda _: confirmation_page.generated_theme_preview.is_displayed())
    manage_themes = confirmation_page.click_manage_listing_button()
    # check that the submitted theme appears in the user's themes list
    assert theme_name in manage_themes.addon_list[0].name


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
@pytest.mark.clear_session
def test_delete_all_extensions(selenium, base_url):
    """This test will delete all the extensions submitted above to make sure
    we can start over with this user in the following runs and also for
    verifying that the addon deletion process functions correctly"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    manage_addons = page.click_my_addons_header_link()
    # run the delete steps until all the addons are cleared from the list
    while len(manage_addons.addon_list) > 0:
        addon = manage_addons.addon_list[0]
        edit = addon.click_addon_name()
        manage = edit.click_manage_versions_link()
        delete = manage.delete_addon()
        delete.input_delete_confirmation_string()
        delete.confirm_delete_addon()
