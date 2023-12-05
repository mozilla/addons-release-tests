import pytest

from pages.desktop.frontend.home import Home
from pages.desktop.frontend.search import Search
from pages.desktop.developers.manage_versions import ManageVersions
from scripts import reusables
from scripts import reusable_flows
from pages.desktop.developers.devhub_home import DevHubHome


@pytest.mark.coverage
def test_changing_tag_shelves_at_refresh_tc_id_c1835238(selenium, base_url, wait, variables):
    # Test Case: C1950460 AMO Coverage > Frontend
    """Go to Homepage and observe the tag shelf"""
    homepage = Home(selenium, base_url).open().wait_for_page_to_load()
    before_refresh_shelve_tag = homepage.extensions_with_tag_header.text
    homepage.extensions_with_tag_see_more.click()
    search_page = Search(selenium, base_url).wait_for_page_to_load()
    search_page.firefox_logo.click()
    after_refresh_shelve_tag = homepage.extensions_with_tag_header.text
    assert (
        before_refresh_shelve_tag is not after_refresh_shelve_tag
    )

# @pytest.mark.coverage
# def test_search_result_for_a_new_submitted_addon_tc_id_c1835241(selenium, base_url, wait, variables):
#     # Test Case: C1835241 AMO Coverage > Frontend
#     """Submit a new listed addon"""
#     devhub_page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
#     devhub_page.devhub_login("developer")
#     addon_slug = reusable_flows.submit_listed_addon_method(selenium, base_url)
#     devhub_page.logout()
#     """Addon is submitted successfully"""
#     """As a reviewer/admin approve the addon"""
#
#     """The addon is approved and becomes public"""
#     manage_versions_page = ManageVersions(selenium, base_url)
#     manage_versions_page.open_manage_versions_page_for_addon(selenium, base_url, addon_slug)
#     manage_versions_page.wait_for_page_to_load()
#     manage_versions_page.wait_for_version_autoapproval("Approved")
#     search_page = Search(selenium, base_url).open().wait_for_page_to_load()
#     search_page.search_box.send_keys(f"{addon_slug}")
#     search_results = search_page.auto_complete_list[0]
#     assert (
#         addon_slug in search_results
#     )
