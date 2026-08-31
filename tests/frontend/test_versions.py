"""A python file that contains tests about versions, licenses"""
from datetime import datetime

import pytest
import requests

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.frontend.versions import Versions
from scripts import reusables
from scripts.addon_install import accept_popup_notification


@pytest.mark.nondestructive
def test_addon_name_in_header(selenium, base_url, variables):
    """Tests that the add-on name appears correctly in the page header."""
    selenium.get(variables["addon_version_page_url"])
    page = Versions(selenium, base_url)
    addon_name = page.versions_page_header.text.split()[0]
    addon_detail_page = page.rating_card.click_addon_title()
    assert addon_name in addon_detail_page.name


@pytest.mark.nondestructive
def test_versions_counter(selenium, base_url, variables):
    """this test verifies that the number of versions displayed
        in the header is the same as the number of elements in the version list"""
    selenium.get(variables["addon_version_page_url"])
    page = Versions(selenium, base_url)
    text = page.versions_page_header.text
    text = text.split("-")[-1][1:]
    text = text.split("versions")[0][:-1]
    assert int(text) == len(page.versions_list)


@pytest.mark.nondestructive
def test_notice_message(selenium, base_url, variables):
    """Tests that notice or warning messages are shown appropriately."""
    selenium.get(variables["addon_version_page_url"])
    page = Versions(selenium, base_url)
    assert page.notice_message.is_displayed()
    assert variables["version_page_notice_message"] in page.notice_message.text


@pytest.mark.nondestructive
def test_ratings_card(selenium, base_url, variables):
    """Tests that the ratings card displays properly on the add-on page."""
    selenium.get(variables["addon_version_page_url"])
    page = Versions(selenium, base_url)
    # verify if ratings card is present
    assert page.rating_card.root.is_displayed()


@pytest.mark.nondestructive
def test_license_link(selenium, base_url, variables):
    """Tests that the license link is present and navigates correctly."""
    selenium.get(variables["addon_version_page_url"])
    page = Versions(selenium, base_url)

    for i in range(len(page.versions_list)):
        if page.versions_list[i].license_link is not False:  # if link exists
            if (
                page.versions_list[i].license_link.text == "Custom License"
            ):  # if link exists and is 'Custom License'
                page.versions_list[i].license_link.click()
                page.wait.until(
                    EC.visibility_of_element_located(
                        (By.CLASS_NAME, "AddonInfo-info-html")
                    )
                )

            else:  # if link exists and is not 'Custom License'
                expected_link = page.versions_list[i].license_link.get_attribute("href")
                if "http" or "https" in expected_link:
                    # full url example-> https://example.com/something/something
                    # turn into-> example.com/something/something
                    expected_link = expected_link.split("//")[1]
                    # turn into-> example.com
                expected_link = expected_link.split("/")[0]
                page.versions_list[i].license_link.click()
                assert expected_link in selenium.current_url

            # in both cases, we go back
            page.driver.back()
            page.driver.refresh()
        else:  # if link does not exist
            assert "All Rights Reserved" in page.versions_list[i].license_text


@pytest.mark.nondestructive
def test_current_version(selenium, base_url, variables):
    """Tests that the current version information is shown accurately."""
    addon_url = f'addon/{variables["addon_version_install"]}/'
    # get info from api
    response = requests.get(f"{base_url}/api/v5/addons/{addon_url}")
    addon_version = response.json()["current_version"]["version"]
    addon_size = reusables.convert_bytes(
        response.json()["current_version"]["file"]["size"]
    )
    api_date = response.json()["current_version"]["file"]["created"][:10]
    # process the date to have the same format as in frontend
    api_date = datetime.strptime(api_date, "%Y-%m-%d")
    # build the date without a leading zero on the day in a cross-platform way;
    # `%#d` (Windows) and `%-d` (Linux/macOS) are not portable, so format the
    # day explicitly to match how the frontend renders it (e.g. "Jul 5, 2020")
    api_processed_date = f"{api_date.strftime('%b')} {api_date.day}, {api_date.year}"
    # verify info displayed in page
    page = Versions(selenium, base_url)
    selenium.get(f'{base_url}/addon/{variables["addon_version_install"]}/versions/')
    assert page.versions_list[0].version_number == addon_version
    assert addon_size == page.versions_list[0].version_size
    assert page.versions_list[0].released_date == api_processed_date


@pytest.mark.nondestructive
def test_version_install_warning(selenium, base_url, variables):
    """Tests that install warnings appear for specific versions when required."""
    selenium.get(
        f'{base_url}/en-US/firefox/addon/{variables["non_recommended_addon"]}/versions/'
    )
    page = Versions(selenium, base_url).wait_for_page_to_load()
    for version in page.versions_list:
        assert variables["install_warning_message"] in version.warning_message.text
        # the 'Learn more' button opens the add-on badges article on SUMO in a
        # new tab. Only the link target is checked: SUMO answers automated
        # browsers with an anti-bot challenge page, so the article itself never
        # finishes loading here
        assert "support.mozilla.org/kb/add-on-badges" in (
            version.warning_learn_more_button.get_attribute("href")
        )


@pytest.mark.nondestructive
def test_add_to_firefox_button(
    selenium, base_url, variables, firefox, firefox_notifications
):
    """Tests the visibility and functionality of the 'Add to Firefox' button."""
    # only the latest version card carries an install button, and the add-on
    # has to be one that is signed for the environment under test - the add-on
    # the other version tests use cannot be installed
    selenium.get(f'{base_url}/addon/{variables["install_extension_slug"]}/versions/')
    page = Versions(selenium, base_url).wait_for_page_to_load()
    latest_version = page.versions_list[0]
    latest_version.add_to_firefox_button.click()
    confirmation = firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    )
    accept_popup_notification(selenium, confirmation)
    complete = firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    )
    accept_popup_notification(selenium, complete)
    # check if add button changed into remove button
    assert "Remove" in latest_version.add_to_firefox_button_text
    # click remove button
    latest_version.add_to_firefox_button.click()
    # check if remove button changed back into add button
    assert "Add" in latest_version.add_to_firefox_button_text


@pytest.mark.nondestructive
def test_version_download_file(
    selenium, base_url, variables, firefox, firefox_notifications
):
    """In Firefox, Download File for older versions will trigger an installation"""
    # the older versions of the add-on used by the other version tests are
    # signed with a root this environment rejects, so Firefox refuses them as
    # corrupt; use the add-on that is signed for the environment under test
    selenium.get(f'{base_url}/addon/{variables["install_extension_slug"]}/versions/')
    page = Versions(selenium, base_url).wait_for_page_to_load()
    # older version cards offer a download link rather than an install button
    page.versions_list[1].click_download_link()
    confirmation = firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    )
    accept_popup_notification(selenium, confirmation)
    complete = firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    )
    accept_popup_notification(selenium, complete)
    # go to the addon detail page and check that the button states have changed
    addon_detail = page.rating_card.click_addon_title()
    # check if add button changed into remove button
    assert "Remove" in addon_detail.button_text
    # click Remove button (is the same as the install button)
    addon_detail.install()
    # check if remove button changed back into add button
    assert "Add to Firefox" in addon_detail.button_text
