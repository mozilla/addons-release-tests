import time
import pytest

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from pages.desktop.frontend.details import Detail
from pages.desktop.frontend.home import Home
from pages.desktop.frontend.search import Search


# Tests covering search suggestions (autocomplete)
from scripts.reusables import get_random_string


@pytest.mark.sanity
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "term",
    [
        "Flagfox",
        "Video DownloadHelper",
        "Adblock Plus",
        "Facebook Container (cas-cur)",
        "Tree Style Tab",
        "Two little birds",
    ],
)
def test_search_suggestion_term_is_higher_tc_id_c4481(base_url, selenium, variables, term):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    suggestions = page.search.search_for(term, execute=False)
    assert suggestions[0].name == term


@pytest.mark.nondestructive
def test_special_chars_dont_break_suggestions_tc_id_c4489(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = variables["search_term"]
    special_chars_term = f"${term[:4]}ç{term[4:]}%ç√®å"
    suggestions = page.search.search_for(special_chars_term, execute=False)
    results = [item.name for item in suggestions]
    assert term in results


@pytest.mark.xfail(
    reason="There is an issue with search on stage - #16610", strict=False
)
@pytest.mark.nondestructive
def test_uppercase_has_same_suggestions_tc_id_c4491(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = variables["search_term"]
    first_suggestions_list = page.search.search_for(term, execute=False)
    first_results = [item.name for item in first_suggestions_list]
    page.search.search_field.clear()
    second_suggestions_list = page.search.search_for(term.upper(), execute=False)
    # Sleep to let autocomplete update.
    time.sleep(2)
    second_results = [item.name for item in second_suggestions_list]
    assert first_results == second_results


@pytest.mark.nondestructive
def test_esc_key_closes_suggestion_list_tc_id_c4486(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = variables["search_term"]
    page.search.search_for(term, execute=False)
    action = ActionChains(selenium)
    # Send ESC key to browser
    action.send_keys(Keys.ESCAPE).perform()
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, "AutoSearchInput-suggestions-list")


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_click_aside_closes_suggestion_list(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = variables["search_term"]
    page.search.search_for(term, execute=False)
    action = ActionChains(selenium)
    action.move_to_element(page.primary_hero).click().perform()
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, "AutoSearchInput-suggestions-list")


@pytest.mark.skip(reason="this test requires more optimization")
@pytest.mark.nondestructive
def test_long_terms_dont_break_suggestions(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = "videodo"
    suggestions = page.search.search_for(term, execute=False)
    # Sleep to let autocomplete update.
    term_max_len = 33
    suggestion_names = [item.name for item in suggestions]
    for suggestion_name in suggestion_names:
        assert len(suggestion_name) <= term_max_len


@pytest.mark.nondestructive
def test_suggestions_change_by_query_tc_id_c4487(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = "pass"
    suggestions = page.search.search_for(term, execute=False)
    first_suggestions_list = [item.name for item in suggestions]
    new_term = "word"
    suggestions = page.search.search_for(new_term, execute=False)
    # allows for search suggestions to update
    time.sleep(2)
    second_suggestions_list = [item.name for item in suggestions]
    assert first_suggestions_list != second_suggestions_list


@pytest.mark.nondestructive
def test_select_result_with_enter_key_tc_id_c4484(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = variables["search_term"]
    page.search.search_for(term, execute=False)
    action = ActionChains(selenium)
    action.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    # give time to the detail page to load
    page.wait_for_title_update(term)
    detail = Detail(selenium, base_url)
    detail.wait_for_page_to_load()
    assert term in detail.name


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_select_result_with_click_tc_id_c4485(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = variables["search_term"]
    suggestions = page.search.search_for(term, execute=False)
    result = suggestions[0].root
    action = ActionChains(selenium)
    action.move_to_element(result).click().perform()
    # give time to the detail page to load
    page.wait_for_title_update(term)
    detail = Detail(selenium, base_url)
    detail.wait_for_page_to_load()
    assert term in detail.name


@pytest.mark.nondestructive
def test_suggestion_icon_is_displayed(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = variables["search_term"]
    suggestions = page.search.search_for(term, execute=False)
    assert suggestions[0].addon_icon.is_displayed()


@pytest.mark.nondestructive
def test_recommended_icon_is_displayed(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = variables["search_term"]
    suggestions = page.search.search_for(term, execute=False)
    assert "Recommended" in suggestions[0].promoted_icon


@pytest.mark.nondestructive
def test_selected_result_is_highlighted(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = variables["search_term"]
    suggestions = page.search.search_for(term, execute=False)
    result = suggestions[0].root
    action = ActionChains(selenium)
    action.move_to_element(result).click_and_hold().perform()
    assert page.search.highlighted_suggestion


@pytest.mark.nondestructive
def test_search_box_character_limit(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    # put 100 characters into term
    term = get_random_string(100)
    search = page.search.search_for(term)
    assert term in search.results_info.text.split('"')[-2]
    # make longer_term have 101 characters
    longer_term = term + "e"
    page.search.search_field.send_keys(longer_term)
    # verify that not all 101 characters were accepted
    assert page.search.search_field.text != longer_term
    page.search.search_field.clear()
    search = page.search.search_for(longer_term)
    # verify the search went for only the first 100 characters
    assert search.results_info.text.split('"')[-2] in term


# Tests covering search results page"
@pytest.mark.sanity
@pytest.mark.nondestructive
def test_search_loads_and_navigates_to_correct_page(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    addon_name = page.recommended_extensions.list[0].name.text
    search = page.search.search_for(addon_name)
    search.wait_for_contextcard_update(addon_name)
    search_name = search.result_list.search_results[0].name
    assert addon_name in search_name
    assert search_name in search.result_list.search_results[0].name


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_blank_search_loads_results_tc_id_c97496(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    search_page = page.search.search_for("", execute=True)
    results = search_page.result_list.search_results
    assert len(results) == 25
    for result in results:
        assert result.promoted_badge
    sort = "users"
    results = [
        getattr(result, sort) for result in search_page.result_list.search_results
    ]
    assert sorted(results, reverse=True) == results


@pytest.mark.nondestructive
def test_search_pagination(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    search_page = page.search.search_for("", execute=True)
    search_page.next_page()
    assert "2" in search_page.page_number
    search_page.previous_page()
    assert "1" in search_page.page_number


# Tests covering search filtering
@pytest.mark.nondestructive
def test_filter_default(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = variables["search_term"]
    page.search.search_for(term)
    search_page = Search(selenium, base_url).wait_for_page_to_load()
    select = Select(search_page.filter_by_sort)
    assert select.first_selected_option.text == "Relevance"
    select = Select(search_page.filter_by_type)
    assert select.first_selected_option.text == "All"
    select = Select(search_page.filter_by_badging)
    assert select.first_selected_option.text == "Any"


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_filter_by_users_tc_id_c92462(base_url, selenium):
    Home(selenium, base_url).open().wait_for_page_to_load()
    term = "fox"
    sort = "users"
    selenium.get(f"{base_url}/search/?&q={term}&sort={sort}")
    search_page = Search(selenium, base_url).wait_for_page_to_load()
    results = [
        getattr(result, sort) for result in search_page.result_list.search_results
    ]
    assert sorted(results, reverse=True) == results


@pytest.mark.sanity
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "category, sort_attr", [["Top Rated", "rating"], ["Trending", "hotness"]]
)
def test_filter_by_rating_and_hotness_tc_id_c92462(base_url, selenium, category, sort_attr):
    """Test searching for an addon and sorting."""
    Home(selenium, base_url).open().wait_for_page_to_load()
    addon_name = "fox"
    selenium.get(f"{base_url}/search/?&q={addon_name}&sort={sort_attr}")
    search_page = Search(selenium, base_url).wait_for_page_to_load()
    results = search_page.result_list.search_results
    if sort_attr == "rating":
        for result in search_page.result_list.search_results:
            assert result.rating > 4
    else:
        assert len(results) == 25


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_filter_extensions_tc_id_c92462(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = "fox"
    page.search.search_for(term)
    search_page = Search(selenium, base_url).wait_for_page_to_load()
    select = Select(search_page.filter_by_type)
    select.select_by_value("extension")
    search_page.wait_for_contextcard_update("extensions")
    assert len(search_page.result_list.themes) == 0


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_top_rated_recommended_addons_tc_id_c92462(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    search_page = page.search.search_for(variables["search_term"])
    # apply filters and then search again
    Select(search_page.filter_by_sort).select_by_visible_text("Top Rated")
    Select(search_page.filter_by_type).select_by_visible_text("All")
    Select(search_page.filter_by_badging).select_by_visible_text("Recommended")
    page.search.search_field.clear()
    page.search.search_for("")
    # verify if sort filter applied correctly
    for result in search_page.result_list.search_results:
        assert getattr(result, "rating") > 4
    # verify badge type
    results = search_page.result_list.search_results
    for result in results:
        assert "Recommended" in result.promoted_badge_label


@pytest.mark.nondestructive
def test_top_rated_recommended_extensions_tc_id_c92462(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    search_page = page.search.search_for(variables["search_term"])
    # apply filters and then search again
    Select(search_page.filter_by_sort).select_by_visible_text("Top Rated")
    Select(search_page.filter_by_type).select_by_visible_text("Extension")
    Select(search_page.filter_by_badging).select_by_visible_text("Recommended")
    page.search.search_field.clear()
    page.search.search_for("")
    # verify if sort filter applied correctly
    for result in search_page.result_list.search_results:
        assert getattr(result, "rating") >= 4
    # verify that no themes are displayed
    assert len(search_page.result_list.themes) == 0
    # verify badge type
    results = search_page.result_list.search_results
    for result in results:
        assert "Recommended" in result.promoted_badge_label


@pytest.mark.nondestructive
def test_top_rated_recommended_themes_tc_id_c92462(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    search_page = page.search.search_for(variables["search_term"])
    # apply filters and then search again
    Select(search_page.filter_by_sort).select_by_visible_text("Top Rated")
    Select(search_page.filter_by_type).select_by_visible_text("Theme")
    Select(search_page.filter_by_badging).select_by_visible_text("Recommended")
    page.search.search_field.clear()
    page.search.search_for("")
    # verify if sort filter applied correctly
    for result in search_page.result_list.search_results:
        assert getattr(result, "rating") >= 4
    # verify that all elements are themes
    assert len(search_page.result_list.themes) == len(
        search_page.result_list.search_results
    )
    # verify badge type
    results = search_page.result_list.search_results
    for result in results:
        assert "Recommended" in result.promoted_badge_label


@pytest.mark.nondestructive
def test_most_users_recommended_addons_tc_id_c92462(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    search_page = page.search.search_for("")
    # apply filters and then search term
    Select(search_page.filter_by_sort).select_by_visible_text("Most Users")
    Select(search_page.filter_by_type).select_by_visible_text("All")
    Select(search_page.filter_by_badging).select_by_visible_text("Recommended")
    page.search.search_for(variables["search_term"])
    # verify if elements are correctly sorted
    results = [
        getattr(result, "users") for result in search_page.result_list.search_results
    ]
    assert sorted(results, reverse=True) == results
    # verify badge type
    results = search_page.result_list.search_results
    for result in results:
        assert "Recommended" in result.promoted_badge_label


@pytest.mark.nondestructive
def test_most_users_by_firefox_addons_tc_id_c92462(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    search_page = page.search.search_for("")
    # apply filters and then search term
    Select(search_page.filter_by_sort).select_by_visible_text("Most Users")
    Select(search_page.filter_by_type).select_by_visible_text("All")
    Select(search_page.filter_by_badging).select_by_visible_text("By Firefox")
    page.search.search_for(variables["search_term"])
    # verify if elements are correctly sorted
    results = [
        getattr(result, "users") for result in search_page.result_list.search_results
    ]
    assert sorted(results, reverse=True) == results
    # verify badge type
    results = search_page.result_list.search_results
    for result in results:
        assert "By Firefox" in result.promoted_badge_label


@pytest.mark.nondestructive
def test_filter_themes(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = "fox"
    page.search.search_for(term)
    search_page = Search(selenium, base_url).wait_for_page_to_load()
    select = Select(search_page.filter_by_type)
    select.select_by_value("statictheme")
    search_page.wait_for_contextcard_update("themes")
    assert len(search_page.result_list.themes) == 25


@pytest.mark.sanity
@pytest.mark.parametrize(
    "sort_attr, title",
    [
        ["recommended", "Recommended"],
        ["line", "by Firefox"],
        ["sponsored,verified", "Verified"],
        ["badged", "Reviewed"],
    ],
)
@pytest.mark.nondestructive
def test_filter_promoted(base_url, selenium, sort_attr, title):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    term = ""
    page.search.search_for(term)
    search_page = Search(selenium, base_url).wait_for_page_to_load()
    select = Select(search_page.filter_by_badging)
    select.select_by_value(sort_attr)
    search_page.wait_for_contextcard_update("results found")
    results = search_page.result_list.search_results
    for result in results:
        assert result.promoted_badge
        if title != "Reviewed":
            assert title.title() in result.promoted_badge_label
