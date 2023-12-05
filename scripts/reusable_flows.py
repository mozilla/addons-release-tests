from pages.desktop.developers.devhub_home import DevHubHome
from scripts import reusables

def submit_listed_addon_method(selenium, base_url):
    devhub_page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    submit_addon = devhub_page.click_submit_addon_button()
    submit_addon.select_listed_option()
    submit_addon.click_continue()
    submit_addon.upload_addon("listed-addon.zip")
    submit_addon.is_validation_successful()
    assert submit_addon.success_validation_message.is_displayed()
    source = submit_addon.click_continue_upload_button()
    source.select_no_to_omit_source()
    confirmation_page = source.continue_listed_submission()
    random_string = reusables.get_random_string(10)
    summary = reusables.get_random_string(10)
    confirmation_page.set_addon_name(random_string)
    confirmation_page.set_addon_summary(summary)
    confirmation_page.select_categories(1)
    confirmation_page.select_license_options[0].click()
    confirmation_page.submit_addon()
    return f"listed-addon{random_string}"