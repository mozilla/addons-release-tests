from datetime import datetime

import pytest
import requests

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.frontend.versions import Versions


@pytest.mark.nondestructive
def test_addon_name_in_header(selenium, base_url, variables):
    selenium.get(variables['addon_version_page_url'])
    page = Versions(selenium, base_url)
    addon_name = page.versions_page_header.text.split()[0]
    addon_detail_page = page.rating_card.click_addon_title()
    assert addon_name in addon_detail_page.name


@pytest.mark.nondestructive
def test_versions_counter(selenium, base_url, variables):
    # this test verifies that the number of versions displayed
    # in the header is the same as the number of elements in the version list
    selenium.get(variables['addon_version_page_url'])
    page = Versions(selenium, base_url)
    text = page.versions_page_header.text
    text = text.split('-')[-1][1:]
    text = text.split('versions')[0][:-1]
    assert int(text) == len(page.versions_list)


@pytest.mark.nondestructive
def test_notice_message(selenium, base_url, variables):
    selenium.get(variables['addon_version_page_url'])
    page = Versions(selenium, base_url)
    assert page.notice_message.is_displayed()
    assert variables['version_page_notice_message'] in page.notice_message.text


@pytest.mark.nondestructive
def test_ratings_card(selenium, base_url, variables):
    selenium.get(variables['addon_version_page_url'])
    page = Versions(selenium, base_url)
    # verify if ratings card is present
    assert page.rating_card.root.is_displayed()


@pytest.mark.nondestructive
def test_license_link(selenium, base_url, variables):
    selenium.get(variables['addon_version_page_url'])
    page = Versions(selenium, base_url)

    for i in range(len(page.versions_list)):
        if page.versions_list[i].license_link is not False:  # if link exists

            if (
                page.versions_list[i].license_link.text == 'Custom License'
            ):  # if link exists and is 'Custom License'
                page.versions_list[i].license_link.click()
                page.wait.until(
                    EC.visibility_of_element_located(
                        (By.CLASS_NAME, 'AddonInfo-info-html')
                    )
                )

            else:  # if link exists and is not 'Custom License'
                expected_link = page.versions_list[i].license_link.get_attribute('href')
                if 'http' or 'https' in expected_link:
                    # full url example-> https://example.com/something/something
                    # turn into-> example.com/something/something
                    expected_link = expected_link.split('//')[1]
                    # turn into-> example.com
                expected_link = expected_link.split('/')[0]
                page.versions_list[i].license_link.click()
                assert expected_link in selenium.current_url

            # in both cases, we go back
            page.driver.back()
            page.driver.refresh()
        else:  # if link does not exist
            assert 'All Rights Reserved' in page.versions_list[i].license_text


@pytest.mark.nondestructive
def test_current_version(selenium, base_url, variables):
    addon_url = 'addon/devhub-listed-ext-07-30/'
    # get info from api
    response = requests.get(f'{base_url}/api/v5/addons/{addon_url}')
    addon_version = response.json()['current_version']['version']
    addon_size_kb = (
        str(round(response.json()['current_version']['file']['size'] / 1024, 2)) + ' KB'
    )
    api_date = response.json()['current_version']['file']['created'][:10]
    # process the date to have the same format as in frontend
    api_date = datetime.strptime(api_date, '%Y-%m-%d')
    api_processed_date = datetime.strftime(api_date, "%b %#d, %Y")
    # verify info displayed in page
    page = Versions(selenium, base_url)
    selenium.get(variables['addon_version_page_url'])
    assert page.versions_list[0].version_number == addon_version
    assert addon_size_kb == page.versions_list[0].version_size
    assert page.versions_list[0].released_date == api_processed_date


@pytest.mark.nondestructive
def test_version_install_warning(selenium, base_url, variables):
    selenium.get(
        f'{base_url}/en-US/firefox/addon/{variables["non_recommended_addon"]}/versions/'
    )
    page = Versions(selenium, base_url)
    for version in page.versions_list:
        assert variables["install_warning_message"] in version.warning_message.text
        version.warning_learn_more_button.click()
        page.driver.switch_to.window(page.driver.window_handles[1])
        page.wait_for_title_update('Add-on Badges')
        page.driver.switch_to.window(page.driver.window_handles[0])


@pytest.mark.nondestructive
def test_add_to_firefox_button(
    selenium, base_url, variables, firefox, firefox_notifications
):
    selenium.get(variables['addon_version_page_url'])
    page = Versions(selenium, base_url)
    page.versions_list[0].add_to_firefox_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    # check if add button changed into remove button
    assert 'Remove' in page.versions_list[0].add_to_firefox_button.text
    # click remove button
    page.versions_list[0].add_to_firefox_button.click()
    # check if remove button changed back into add button
    assert 'Add' in page.versions_list[0].add_to_firefox_button.text
