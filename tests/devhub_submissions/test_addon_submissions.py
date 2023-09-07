import pytest

from pages.desktop.developers.devhub_home import DevHubHome
from pages.desktop.developers.manage_versions import ManageVersions
from pages.desktop.developers.submit_addon import (
    SubmitAddon,
    SubmissionConfirmationPage,
)
from scripts import reusables
from api import api_helpers, payloads

@pytest.mark.login("regular_user")
def test_devhub_developer_agreement_page_contents(selenium, base_url, variables, wait):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # use an account that hasn't accepted the agreement before
    # page.devhub_login('regular_user')
    page.wait_for_page_to_load()
    dist_agreement = page.click_submit_theme_button()
    assert (
        variables['devhub_submit_addon_agreement_header']
        in dist_agreement.submission_form_subheader.text
    )
    assert (
        variables['distribution_page_explainer']
        in dist_agreement.distribution_page_explainer
    )
    assert (
        'Firefox Add-on Distribution Agreement'
        in dist_agreement.distribution_agreement_article_link.text
    )
    assert (
        'Review Policies and Rules' in dist_agreement.review_policies_article_link.text
    )
    assert variables['distribution_user_consent'] in dist_agreement.user_consent_text
    wait.until(lambda _: dist_agreement.recaptcha.is_displayed())
    # clicking on Cancel agreement should redirect to Devhub Homepage
    dist_agreement.cancel_agreement.click()
    page = DevHubHome(selenium, base_url).wait_for_page_to_load()
    assert page.page_logo.is_displayed()

@pytest.mark.create_session("regular_user")
def test_devhub_developer_agreement_page_links(selenium, base_url):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # use an account that hasn't accepted the agreement before
    # page.devhub_login('regular_user')
    dist_agreement = page.click_submit_theme_button()
    # check that the distribution agreement link opens the correct Extension workshop page
    dist_agreement.click_extension_workshop_article_link(
        dist_agreement.distribution_agreement_article_link,
        'Firefox Add-on Distribution Agreement',
    )
    # check that the review policies link opens the correct Extension workshop page
    dist_agreement.click_extension_workshop_article_link(
        dist_agreement.review_policies_article_link, 'Add-on Policies'
    )
    # verify that the Dev Account info link opens an Extension Workshop article page
    dist_agreement.click_dev_accounts_info_link()

@pytest.mark.create_session("regular_user")
def test_devhub_developer_agreement_checkboxes(selenium, base_url):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # use an account that hasn't accepted the agreement before
    page.devhub_login('regular_user')
    dist_agreement = page.click_submit_theme_button()
    dist_agreement.distribution_agreement_checkbox.click()
    assert dist_agreement.distribution_agreement_checkbox.is_selected()
    dist_agreement.review_policies_checkbox.click()
    assert dist_agreement.review_policies_checkbox.is_selected()
    dist_agreement.click_recaptcha_checkbox()

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

@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
def test_verify_first_version_autoapproval(selenium, base_url, variables, wait):
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
    submit_addon.upload_addon('listed-addon.zip')
    # waits for the validation to complete and checks that is successful
    submit_addon.is_validation_successful()
    # checking that the Firefox compatibility checkbox is selected by default
    assert submit_addon.firefox_compat_checkbox.is_selected()
    # select the Android compatibility checkbox
    submit_addon.android_compat_checkbox.click()
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

@pytest.mark.sanity
@pytest.mark.serial
def test_verify_new_unlisted_version_autoapproval(selenium, base_url, variables):
    """Uploads a new version to an existing addon and verifies that is auto-approved"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login('developer')
    addon = variables['unlisted_new_version_auto_approval']
    # in order to upload a new version, we need to increment on the existing version number
    # to obtain the current version number, we make an API request that returns the value
    auth = selenium.get_cookie('sessionid')['value']
    version_string = api_helpers.get_addon_version_string(base_url, addon, auth)
    # create a new addon version with the incremented versio number
    manifest = {
        'manifest_version': 2,
        'theme': {'frame': '#083af0', 'tab_background_text': '#ffffff'},
        'version': f'{float(version_string) + 1}',
        'name': 'New version auto-approval',
    }
    api_helpers.make_addon(manifest)
    # go to the unlisted distribution page to submit a new version
    selenium.get(f'{base_url}/developers/addon/{addon}/versions/submit/')
    submit_version = SubmitAddon(selenium).wait_for_page_to_load()
    submit_version.upload_addon('make-addon.zip')
    # wait for the validation to finish and check if it is successful
    submit_version.is_validation_successful()
    assert submit_version.success_validation_message.is_displayed()
    submit_version.click_continue()
    confirmation_page = SubmissionConfirmationPage(selenium)
    assert (
        variables['unlisted_submission_confirmation']
        in confirmation_page.submission_confirmation_messages[0].text
    )
    # open the manage versions page for the addon and wait for the latest version to be auto-approved
    selenium.get(f'{base_url}/developers/addon/{addon}/versions')
    version_status = ManageVersions(selenium).wait_for_page_to_load()
    version_status.wait_for_version_autoapproval('Approved')

@pytest.mark.create_session("submissions_user")
def test_addon_distribution_page_contents(selenium, base_url, variables, wait):
    """Check the elements present on devhub addon distribution page (where the user selects
    the listed or unlisted channels to upload their addon"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # page.devhub_login('submissions_user')
    dist_page = page.click_submit_theme_button()
    wait.until(lambda _: dist_page.submission_form_header.is_displayed())
    assert (
        variables['devhub_submit_addon_distribution_header']
        in dist_page.submission_form_subheader.text
    )
    # checks that the listed option is selected by default
    assert dist_page.listed_option_radiobutton.is_selected()
    assert variables['listed_option_helptext'] in dist_page.listed_option_helptext
    assert (
        variables['unlisted_option_helptext'] in dist_page.unlisted_option_helptext.text
    )
    # check that the 'update_url', 'distribution' and 'policies' links opens the correct Extension Workshop page
    dist_page.click_extension_workshop_article_link(
        dist_page.update_url_link, 'Updating your extension'
    )
    assert (
        variables['distribution_and_signing_helptext']
        in dist_page.distribution_and_signing_helptext.text
    )
    dist_page.click_extension_workshop_article_link(
        dist_page.distribution_and_signing_link, 'Signing and distributing your add-on'
    )
    assert (
        variables['addon_policies_helptext'] in dist_page.addon_policies_helptext.text
    )
    dist_page.click_extension_workshop_article_link(
        dist_page.addon_policies_link, 'Add-on Policies'
    )

@pytest.mark.create_session("submissions_user")
def test_devhub_upload_extension_page_contents(selenium, base_url, wait, variables):
    """Verify the elements present on the upload file page, where the user
    uploads and validates an addon file"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # page.devhub_login('submissions_user')
    selenium.get(f'{base_url}/developers/addon/submit/theme/upload-listed')
    upload_page = SubmitAddon(selenium, base_url).wait_for_page_to_load()
    upload_page.developer_notification_box.is_displayed()
    assert (
        variables['upload_extension_file_helptext']
        in upload_page.file_upload_helptext[0].text
    )
    assert variables['create_theme_version_helptext'] in upload_page.accepted_file_types

@pytest.mark.create_session("submissions_user")
def test_upload_unsupported_file_validation_error(selenium, base_url, wait):
    """Verify validation results for errors triggered by unsupported file uploads"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # page.devhub_login('submissions_user')
    selenium.get(f'{base_url}/developers/addon/submit/upload-listed')
    upload_page = SubmitAddon(selenium, base_url).wait_for_page_to_load()
    file = 'tar-ext.tar'
    upload_page.upload_addon(file)
    wait.until(lambda _: upload_page.failed_validation_bar.is_displayed())
    # check that the validation results show the following 'error specific' components
    assert f'Error with {file}' in upload_page.validation_status_title
    upload_page.click_validation_support_link()
    assert 'Your add-on failed validation' in upload_page.validation_failed_message
    assert (
        "The filetype you uploaded isn't recognized"
        in upload_page.validation_failed_reason[0].text
    )

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

@pytest.mark.parametrize(
    'addon_name, description',
    (
        ['这是我的名字', '这是我的描述'],
        ['1515هذا هو اسمي', 'هذا هو وصفي'],
        ['이건 내 이름이야', '이것은 내 설명입니다'],
        ['ဒါက ငါ့နာမည်ပါ။', 'ဤသည်မှာ ကျွန်ုပ်၏ ဖော်ပြချက်ဖြစ်ပါသည်။'],
        ['ʌɑ:æčβぁŇ', '☺️ʌɑ:æčβぁŇ☺️'],
    ),
    ids=[
        'Chinese characters',
        'Arabic characters',
        'Korean characters',
        'Burmese characters',
        'Random non-ascii characters',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
def test_submit_unicode_addon(
    selenium, base_url, variables, wait, addon_name, description
):
    """Test covering the process of uploading addons with non-ASCII characters"""
    manifest = {
        **payloads.minimal_manifest,
        'name': addon_name,
        'description': description,
    }
    api_helpers.make_addon(manifest)
    selenium.get(f'{base_url}/developers/addon/submit/upload-listed')
    submit_addon = SubmitAddon(selenium, base_url).wait_for_page_to_load()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_addon.firefox_compat_checkbox.is_selected())
    submit_addon.upload_addon('make-addon.zip')
    # waits for the validation to complete and checks that is successful
    submit_addon.is_validation_successful()
    # on submit source code page, select 'No' to upload source code
    source = submit_addon.click_continue_upload_button()
    source.select_no_to_omit_source()
    details_form = source.continue_listed_submission()
    details_form.select_firefox_categories(0)
    # set an addon license from the available list
    details_form.select_license_options[0].click()
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
def test_addon_validation_warning(selenium, base_url, variables, wait):
    """Test validation results when addons trigger some warnings"""
    selenium.get(f'{base_url}/developers/addon/submit/upload-listed')
    submit_addon = SubmitAddon(selenium, base_url).wait_for_page_to_load()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_addon.firefox_compat_checkbox.is_selected())
    submit_addon.upload_addon('validation-warning.zip')
    submit_addon.is_validation_successful()
    assert (
        variables['addon_validation_warning'] in submit_addon.validation_warning_message
    )
    # click on the validation results link to open the validation summary page
    results = submit_addon.click_validation_summary()
    assert (
        'Validation Results for validation-warning.zip'
        in results.validation_results_header
    )
    assert results.validation_summary_shelf.is_displayed()
    assert results.validation_general_results.is_displayed()
    assert results.validation_security_results.is_displayed()
    assert results.validation_extension_results.is_displayed()
    assert results.validation_localization_results.is_displayed()
    assert results.validation_compatibility_results.is_displayed()


@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
def test_cancel_and_disable_version_during_upload(selenium, base_url, wait):
    """Test what happens in the upload process when a user chooses to cancel the submission"""
    selenium.get(f'{base_url}/developers/addon/submit/upload-listed')
    submit_addon = SubmitAddon(selenium, base_url).wait_for_page_to_load()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_addon.firefox_compat_checkbox.is_selected())
    submit_addon.upload_addon('listed-addon.zip')
    submit_addon.is_validation_successful()
    source = submit_addon.click_continue_upload_button()
    # on the source code page click on the "Cancel and Disable version' button
    source.click_cancel_and_disable_version()
    assert (
        'Are you sure you wish to cancel and disable version?'
        in source.cancel_and_disable_explainer_text
    )
    # click on do not cancel to close the modal
    source.click_do_not_cancel_version()
    # click cancel version again and confirm this time
    source.click_cancel_and_disable_version()
    canceled_version = source.confirm_cancel_and_disable_version()
    assert 'Incomplete' in canceled_version.incomplete_status.text
    assert 'Disabled by Mozilla' in canceled_version.version_approval_status[0].text
    # delete the incomplete submission
    delete = canceled_version.delete_addon()
    delete.input_delete_confirmation_string()
    delete.confirm_delete_addon()


@pytest.mark.sanity
def test_submit_listed_wizard_theme(selenium, base_url, variables, wait, delete_themes):
    """A test that checks a straight-forward theme submission with the devhub wizard"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login("submissions_user")
    submit_addon = page.click_submit_theme_button()
    # start the upload for a listed theme
    submit_addon.select_listed_option()
    submit_addon.click_continue()
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