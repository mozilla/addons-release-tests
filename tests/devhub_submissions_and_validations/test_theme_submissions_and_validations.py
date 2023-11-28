import pytest

from pages.desktop.developers.devhub_home import DevHubHome
from pages.desktop.developers.submit_addon import (
    SubmitAddon
)
from scripts import reusables
from api import api_helpers, payloads


@pytest.mark.theme_and_validation
def test_devhub_developer_agreement_page_contents(selenium, base_url, variables, wait):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login("regular_user")
    page.wait_for_page_to_load()
    dist_agreement = page.click_submit_theme_button()
    assert (
            variables["devhub_submit_addon_agreement_header"]
            in dist_agreement.submission_form_subheader.text
    )
    assert (
            variables["distribution_page_explainer"]
            in dist_agreement.distribution_page_explainer
    )
    assert (
            "Firefox Add-on Distribution Agreement"
            in dist_agreement.distribution_agreement_article_link.text
    )
    assert (
            "Review Policies and Rules" in dist_agreement.review_policies_article_link.text
    )
    assert variables["distribution_user_consent"] in dist_agreement.user_consent_text
    wait.until(lambda _: dist_agreement.recaptcha.is_displayed())
    # clicking on Cancel agreement should redirect to Devhub Homepage
    dist_agreement.cancel_agreement.click()
    page = DevHubHome(selenium, base_url).wait_for_page_to_load()
    assert page.page_logo.is_displayed()


@pytest.mark.theme_and_validation
def test_devhub_developer_agreement_page_links(selenium, base_url):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login("regular_user")
    dist_agreement = page.click_submit_theme_button()
    # check that the distribution agreement link opens the correct Extension workshop page
    dist_agreement.click_extension_workshop_article_link(
        dist_agreement.distribution_agreement_article_link,
        "Firefox Add-on Distribution Agreement",
    )
    # check that the review policies link opens the correct Extension workshop page
    dist_agreement.click_extension_workshop_article_link(
        dist_agreement.review_policies_article_link, "Add-on Policies"
    )
    # verify that the Dev Account info link opens an Extension Workshop article page
    dist_agreement.click_dev_accounts_info_link()


@pytest.mark.theme_and_validation
def test_devhub_developer_agreement_checkboxes(selenium, base_url):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login("regular_user")
    # use an account that hasn't accepted the agreement before
    dist_agreement = page.click_submit_theme_button()
    dist_agreement.distribution_agreement_checkbox.click()
    assert dist_agreement.distribution_agreement_checkbox.is_selected()
    dist_agreement.review_policies_checkbox.click()
    assert dist_agreement.review_policies_checkbox.is_selected()
    dist_agreement.click_recaptcha_checkbox()


@pytest.mark.sanity
@pytest.mark.theme_and_validation
@pytest.mark.login("submissions_user")
def test_submit_listed_wizard_theme_tc_id_c97500(selenium, base_url, variables, wait, delete_themes):
    """A test that checks a straight-forward theme submission with the devhub wizard"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # page.devhub_login("submissions_user")
    submit_addon = page.click_submit_theme_button()
    # start the upload for a listed theme
    submit_addon.select_listed_option()
    submit_addon.click_continue()
    create_theme = submit_addon.click_create_theme_button()
    theme_name = f"wizard_theme_{reusables.get_random_string(5)}"
    create_theme.set_theme_name(theme_name)
    create_theme.upload_theme_header("theme_header.png")
    wait.until(lambda _: create_theme.uploaded_image_preview.is_displayed())
    # make a note of the image source uploaded as the theme header
    uploaded_img_source = create_theme.uploaded_image_source
    # verify that the uploaded image is applied in the browser preview
    assert uploaded_img_source == create_theme.browser_preview_image
    theme_details = create_theme.submit_theme()
    # check that the name set earlier carried over
    assert theme_name in theme_details.addon_name_field.get_attribute("value")
    theme_details.set_addon_summary("Theme summary")
    # select a category for the theme
    theme_details.theme_category_abstract.click()
    # set up a license for the theme based on 'Yes'[0]/'No'[1] options
    theme_details.select_theme_licence_sharing_rights(1)
    theme_details.select_theme_license_commercial_use(1)
    theme_details.select_theme_license_creation_rights(1)
    # check that the resulted license is 'All Rights Reserved'
    assert "All Rights Reserved" in theme_details.generated_theme_license.text
    confirmation_page = theme_details.submit_addon()
    # verify that the theme preview has been generated after submission
    wait.until(lambda _: confirmation_page.generated_theme_preview.is_displayed())
    manage_themes = confirmation_page.click_manage_listing_button()
    # check that the submitted theme appears in the user's themes list
    assert theme_name in manage_themes.addon_list[0].name


@pytest.mark.create_session("submissions_user")
@pytest.mark.theme_and_validation
def test_addon_distribution_page_contents_tc_id_c14882(selenium, base_url, variables, wait):
    """Check the elements present on devhub addon distribution page (where the user selects
    the listed or unlisted channels to upload their addon"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    dist_page = page.click_submit_theme_button()
    wait.until(lambda _: dist_page.submission_form_header.is_displayed())
    assert (
            variables["devhub_submit_addon_distribution_header"]
            in dist_page.submission_form_subheader.text
    )
    # checks that the listed option is selected by default
    assert dist_page.listed_option_radiobutton.is_selected()
    assert variables["listed_option_helptext"] in dist_page.listed_option_helptext
    assert (
            variables["unlisted_option_helptext"] in dist_page.unlisted_option_helptext.text
    )
    # check that the 'update_url', 'distribution' and 'policies' links opens the correct Extension Workshop page
    dist_page.click_extension_workshop_article_link(
        dist_page.update_url_link, "Updating your extension"
    )
    assert (
            variables["distribution_and_signing_helptext"]
            in dist_page.distribution_and_signing_helptext.text
    )
    dist_page.click_extension_workshop_article_link(
        dist_page.distribution_and_signing_link, "Signing and distributing your add-on"
    )
    assert (
            variables["addon_policies_helptext"] in dist_page.addon_policies_helptext.text
    )
    dist_page.click_extension_workshop_article_link(
        dist_page.addon_policies_link, "Add-on Policies"
    )


@pytest.mark.create_session("submissions_user")
@pytest.mark.theme_and_validation
def test_devhub_upload_extension_page_contents(selenium, base_url, wait, variables):
    """Verify the elements present on the upload file page, where the user
    uploads and validates an addon file"""
    selenium.get(f"{base_url}/developers/addon/submit/theme/upload-listed")
    upload_page = SubmitAddon(selenium, base_url).wait_for_page_to_load()
    upload_page.developer_notification_box.is_displayed()
    assert (
            variables["upload_extension_file_helptext"]
            in upload_page.file_upload_helptext[0].text
    )
    assert variables["create_theme_version_helptext"] in upload_page.accepted_file_types


@pytest.mark.create_session("submissions_user")
@pytest.mark.theme_and_validation
def test_upload_unsupported_file_validation_error(selenium, base_url, wait):
    """Verify validation results for errors triggered by unsupported file uploads"""
    selenium.get(f"{base_url}/developers/addon/submit/upload-listed")
    upload_page = SubmitAddon(selenium, base_url).wait_for_page_to_load()
    file = "tar-ext.tar"
    upload_page.upload_addon(file)
    wait.until(lambda _: upload_page.failed_validation_bar.is_displayed())
    # check that the validation results show the following 'error specific' components
    assert f"Error with {file}" in upload_page.validation_status_title
    upload_page.click_validation_support_link()
    assert "Your add-on failed validation" in upload_page.validation_failed_message
    assert (
            "The filetype you uploaded isn't recognized"
            in upload_page.validation_failed_reason[0].text
    )


@pytest.mark.parametrize(
    "addon_name, description",
    (
            ["这是我的名字", "这是我的描述"],
            ["1515هذا هو اسمي", "هذا هو وصفي"],
            ["이건 내 이름이야", "이것은 내 설명입니다"],
            ["ဒါက ငါ့နာမည်ပါ။", "ဤသည်မှာ ကျွန်ုပ်၏ ဖော်ပြချက်ဖြစ်ပါသည်။"],
            ["ʌɑ:æčβぁŇ", "☺️ʌɑ:æčβぁŇ☺️"],
    ),
    ids=[
        "Chinese characters",
        "Arabic characters",
        "Korean characters",
        "Burmese characters",
        "Random non-ascii characters",
    ],
)
@pytest.mark.serial
@pytest.mark.theme_and_validation
@pytest.mark.create_session("submissions_user")
def test_submit_unicode_addon_tc_id_c4590(
        selenium, base_url, variables, wait, addon_name, description
):
    """Test covering the process of uploading addons with non-ASCII characters"""
    manifest = {
        **payloads.minimal_manifest,
        "name": addon_name,
        "description": description,
    }
    api_helpers.make_addon(manifest)
    selenium.get(f"{base_url}/developers/addon/submit/upload-listed")
    submit_addon = SubmitAddon(selenium, base_url).wait_for_page_to_load()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_addon.firefox_compat_checkbox.is_selected())
    submit_addon.upload_addon("make-addon.zip")
    # waits for the validation to complete and checks that is successful
    submit_addon.is_validation_successful()
    # on submit source code page, select 'No' to upload source code
    source = submit_addon.click_continue_upload_button()
    source.select_no_to_omit_source()
    details_form = source.continue_listed_submission()
    details_form.select_categories(0)
    # set an addon license from the available list
    details_form.select_license_options[0].click()
    # submit the add-on details
    confirmation_page = details_form.submit_addon()
    assert (
            variables["listed_submission_confirmation"]
            in confirmation_page.submission_confirmation_messages[0].text
    )
    # go to the addon edit listing page and check that it was created
    edit_listing = confirmation_page.click_edit_listing_button()
    assert addon_name in edit_listing.name


@pytest.mark.serial
@pytest.mark.theme_and_validation
@pytest.mark.create_session("submissions_user")
def test_addon_validation_warning_tc_id_c2283005(selenium, base_url, variables, wait):
    """Test validation results when addons trigger some warnings"""
    selenium.get(f"{base_url}/developers/addon/submit/upload-listed")
    submit_addon = SubmitAddon(selenium, base_url).wait_for_page_to_load()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_addon.firefox_compat_checkbox.is_selected())
    submit_addon.upload_addon("validation-warning.zip")
    submit_addon.is_validation_successful()
    assert (
            variables["addon_validation_warning"] in submit_addon.validation_warning_message
    )
    # click on the validation results link to open the validation summary page
    results = submit_addon.click_validation_summary()
    assert (
            "Validation Results for validation-warning.zip"
            in results.validation_results_header
    )
    assert results.validation_summary_shelf.is_displayed()
    assert results.validation_general_results.is_displayed()
    assert results.validation_security_results.is_displayed()
    assert results.validation_extension_results.is_displayed()
    assert results.validation_localization_results.is_displayed()
    assert results.validation_compatibility_results.is_displayed()


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.addon
@pytest.mark.theme_and_validation
@pytest.mark.create_session("submissions_user")
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
