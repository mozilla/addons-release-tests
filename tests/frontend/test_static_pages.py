import pytest
import requests

from selenium.common.exceptions import NoSuchElementException

from pages.desktop.frontend.home import Home
from pages.desktop.frontend.static_pages import StaticPages


@pytest.mark.nondestructive
def test_review_guidelines_page_loaded_correctly(base_url, selenium):
    selenium.get(f"{base_url}/review_guide")
    page = StaticPages(selenium, base_url)
    # verify the tab title
    assert "Review Guidelines – Add-ons for Firefox" in page.driver.title
    # verify the header
    assert "Review Guidelines" in page.page_header
    # verify the paragraphs
    assert "Tips for writing a great review" in page.content.text
    assert "Frequently Asked Questions about Reviews" in page.content.text
    # verify that the links are displayed
    assert page.forum_link.is_displayed()


@pytest.mark.nondestructive
def test_about_firefox_addons_page_loaded_correctly(base_url, selenium, variables):
    selenium.get(f"{base_url}/about")
    page = StaticPages(selenium, base_url)
    # verify the tab title
    assert "About Firefox Add-ons – Add-ons for Firefox" in page.driver.title
    # verify the header
    assert "About Firefox Add-ons" in page.page_header
    # verify the paragraphs
    assert "A community of creators" in page.content.text
    assert "Get involved" in page.content.text
    assert "Report an issue" in page.content.text
    assert "Get support" in page.content.text
    # verify that the links are displayed
    assert page.thunderbird_link.is_displayed()
    assert page.seamonkey_link.is_displayed()
    for link in page.get_involved_links:
        assert link.is_displayed()
    for link in page.report_an_issue_links:
        assert link.is_displayed()
    for link in page.get_support_links:
        assert link.is_displayed()


@pytest.mark.nondestructive
def test_blocked_addon_page_loaded_correctly(base_url, selenium, variables):
    selenium.get(variables["static_page_blocked_addon"])
    page = StaticPages(selenium, base_url)
    # verify the tab title
    assert (
        f'{variables["blocked_addon_name"]} has been blocked for your protection. – Add-ons for Firefox'
        in page.driver.title
    )
    # verify the header
    assert (
        f'{variables["blocked_addon_name"]} has been blocked for your protection.'
        in page.page_header
    )
    # verify the paragraphs
    assert "Why was it blocked?" in page.content.text
    assert "What does this mean?" in page.content.text
    # verify that the links are displayed
    assert page.addon_policies_link.is_displayed()
    assert page.certain_criteria_link.is_displayed()
    assert page.this_support_article_link.is_displayed()


@pytest.mark.nondestructive
def test_blocked_addon_page_does_not_have_login_button(base_url, selenium, variables):
    selenium.get(variables["static_page_blocked_addon"])
    page = StaticPages(selenium, base_url)
    with pytest.raises(NoSuchElementException):
        page.header.login_button.is_displayed()


@pytest.mark.nondestructive
def test_review_guidelines_page_links(base_url, selenium, variables):
    selenium.get(f"{base_url}/review_guide")
    page = StaticPages(selenium, base_url)
    link_domain = page.forum_link.get_attribute("href").split("/")[2].split(".")[0]
    page.forum_link.click()
    page.wait_for_current_url(link_domain)


@pytest.mark.nondestructive
def test_about_firefox_addons_page_links(base_url, selenium, variables):
    selenium.get(f"{base_url}/about")
    page = StaticPages(selenium, base_url)
    for count in range(len(page.page_links)):
        link = page.page_links[count]
        # skip the link for sending an email
        if "mailto" in link.get_attribute("href"):
            continue
        # get the link's domain
        link_domain = link.get_attribute("href").split("/")[2].split(".")[0]
        # click the link
        link.click()
        # verify if the opened page link contains the correct domain
        page.wait_for_current_url(link_domain)
        # go back to test the next link
        page.driver.back()
        page.wait_for_page_to_load()


@pytest.mark.nondestructive
def test_blocked_addon_page_links(base_url, selenium, variables):
    selenium.get(variables["static_page_blocked_addon"])
    page = StaticPages(selenium, base_url)
    for count in range(len(page.page_links)):
        link = page.page_links[count]
        # get the link's domain
        link_domain = link.get_attribute("href").split("/")[2].split(".")[0]
        # click the link
        link.click()
        # verify if the opened page link contains the correct domain
        assert link_domain in selenium.current_url
        # go back to test the next link
        page.driver.back()


@pytest.mark.nondestructive
def test_login_expired_page(base_url, selenium, variables):
    selenium.get(base_url)
    page = Home(selenium, base_url)
    page.login("regular_user")
    # open AMO in a new tab and logout
    page.driver.switch_to.new_window("tab")
    page.driver.get(base_url)
    page.logout()
    # go back to the first tab
    page.driver.switch_to.window(page.driver.window_handles[0])
    # open a detail page for an extension, it should get you to the expired login page
    page.hero_banner.click_hero_extension_link()
    # verify the expired login page
    page = StaticPages(selenium, base_url)
    assert "You have been logged out." in page.notice_messages[-1].text
    assert "Login Expired" in page.page_header
    assert variables["static_page_login_expired_text"] in page.content.text
    # click the link for reloading the page
    page = page.click_reload_page_link
    # verify that an add-on detail page is displayed
    assert page.addon_icon.is_displayed()


@pytest.mark.nondestructive
def test_not_found_page(base_url, selenium, variables):
    # go to an addon detail page that does not exist
    selenium.get(f"{base_url}/addon/§§/")
    page = StaticPages(selenium, base_url)
    assert "Oops! We can’t find that page" in page.page_header
    for count in range(len(page.page_links)):
        link = page.page_links[count]
        # get the link's domain
        link_domain = link.get_attribute("href").split("/")[2].split(".")[0]
        # click the link
        link.click()
        # verify that the page was found (status code != 404)
        r = requests.get(selenium.current_url)
        r.raise_for_status()
        # verify if the opened page link contains the correct domain
        assert link_domain in selenium.current_url
        # go back to test the next link
        page.driver.back()
