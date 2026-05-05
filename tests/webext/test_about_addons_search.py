from urllib.parse import parse_qs, urlparse

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from pages.desktop.about_addons import AboutAddons
from scripts.reusables import get_random_string


def test_about_addons_search_redirects_to_amo_with_query_params(selenium):
    """Searching from the about:addons Extensions panel opens AMO in a new tab
    with the term echoed in the search box and the q/appversion/platform query
    parameters present in the URL."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_extensions_side_button()
    search_term = "addon"

    search_page = about_addons.search_box(search_term)
    search_page.wait_for_contextcard_update(search_term)

    params = parse_qs(urlparse(selenium.current_url).query)
    assert params.get("q") == [search_term], (
        f"Expected URL query param q={search_term!r}, got {params.get('q')}; "
        f"full URL: {selenium.current_url}"
    )
    assert "appversion" in params, (
        f"appversion parameter missing from URL: {selenium.current_url}"
    )
    assert "platform" in params, (
        f"platform parameter missing from URL: {selenium.current_url}"
    )

    amo_search_value = search_page.find_element(
        *search_page._search_box_locator
    ).get_attribute("value")
    assert amo_search_value == search_term, (
        f"AMO search box shows {amo_search_value!r}, expected {search_term!r}"
    )


def test_about_addons_search_default_filters(selenium):
    """The AMO search results page reached from about:addons defaults to
    Sort=Relevance, Add-on type=All, and an OS filter selected per the
    platform sent in the URL."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_extensions_side_button()

    search_page = about_addons.search_box("ad")
    search_page.wait_for_contextcard_update("ad")

    sort_selected = Select(search_page.filter_by_sort).first_selected_option.text
    type_selected = Select(search_page.filter_by_type).first_selected_option.text
    os_selected = Select(search_page.filter_by_os).first_selected_option.text

    assert sort_selected == "Relevance", (
        f"Default Sort filter was {sort_selected!r}, expected 'Relevance'"
    )
    assert type_selected == "All", (
        f"Default Add-on type filter was {type_selected!r}, expected 'All'"
    )

    platform_param = parse_qs(urlparse(selenium.current_url).query).get(
        "platform", [None]
    )[0]
    assert platform_param, (
        f"platform parameter missing from URL: {selenium.current_url}"
    )
    assert os_selected, (
        f"OS filter has no selection despite URL platform={platform_param!r}"
    )


def test_about_addons_search_shows_pagination_for_many_results(selenium):
    """A broad search query that returns more than 25 results displays the
    pagination controls on the AMO results page."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_extensions_side_button()

    search_page = about_addons.search_box("ad")
    search_page.search_results_list_loaded(20)
    assert search_page.is_element_displayed(
        *search_page._pagination_next_locator
    ), "Pagination Next control was not displayed for a broad search query"


def test_about_addons_search_full_addon_name_top_result(selenium, variables):
    """Searching for the complete name of an addon places the matching addon
    at the top of the AMO results list."""
    addon_name = variables["search_term"]
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_extensions_side_button()

    search_page = about_addons.search_box(addon_name)
    search_page.search_results_list_loaded(1)

    top_result = search_page.result_list.search_results[0].name
    assert top_result == addon_name, (
        f"Top AMO result was {top_result!r}, expected exact match {addon_name!r}"
    )


def test_about_addons_search_box_100_char_limit(selenium, wait):
    """The about:addons search field accepts at most 100 characters; submitting
    after typing more sends the truncated value to AMO."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_extensions_side_button()

    long_input = get_random_string(150)
    search_field = about_addons.search_field
    search_field.send_keys(long_input)

    field_value = search_field.get_attribute("value")
    assert len(field_value) == 100, (
        f"Search box accepted {len(field_value)} characters, expected the 100-char cap"
    )
    assert field_value == long_input[:100], (
        "Search box content does not match the first 100 characters of the input"
    )

    search_field.send_keys(Keys.ENTER)
    about_addons.wait.until(
        lambda _: len(selenium.window_handles) == 2,
        message="AMO search did not open in a new tab",
    )
    selenium.switch_to.window(selenium.window_handles[1])

    submitted_q = parse_qs(urlparse(selenium.current_url).query).get("q", [None])[0]
    assert submitted_q == field_value, (
        f"AMO query parameter q={submitted_q!r} did not match the truncated input"
    )
