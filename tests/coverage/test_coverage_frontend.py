import pytest
import time

from pages.desktop.frontend.details import Detail


@pytest.mark.coverage
def test_geo_locations_tc_id_c1781143(selenium, base_url, wait, variables):
    # Test Case:C1781143 AMO Coverage > Require admin tools
    selenium.get(f"{base_url}/firefox/addon/devhub-listed-ext-06-13/")
    detail_page = Detail(selenium, base_url).wait_for_page_to_load()
    time.sleep(3)
    assert(
        variables["page_not_available_in_your_region"]
        in detail_page.page_not_available_in_region.text
    )
    assert (
        variables["page_not_accessible_in_your_region"]
        in detail_page.not_available_in_your_region_message.text
    )
    assert (
        variables["paragraph_with_links"]
        in detail_page.paragraphs_with_links_message.text
    )

@pytest.mark.coverage
def test_blocked_frontend_page_tc_id_c1771696(selenium, base_url, wait, variables):
    # Test Case: C1771696 AMO Coverage > Require admin tools
    selenium.get(f"{base_url}/firefox/blocked-addon/alextest@mail.ro/")
    detail_page = Detail(selenium, base_url).wait_for_page_to_load()
    assert (
        variables["card_header_text"]
        in detail_page.card_header_text.text
    )
    assert (
        variables["why_was_it_blocked"]
        in detail_page.why_was_it_blocked.text
    )
    assert (
        variables["block_metadata"]
        in detail_page.block_metadata.text
    )

