import pytest

from pages.desktop.frontend.home import Home
from pages.desktop.frontend.search import Search



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


