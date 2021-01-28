import pytest
from pages.desktop.search import Search
from pages.desktop.themes import Themes
from selenium.webdriver.support.select import Select


@pytest.mark.desktop_only
@pytest.mark.parametrize(
    'count, category',
    enumerate([
        'Abstract',
        'Causes',
        'Fashion',
        'Film and TV',
        'Firefox',
        'Foxkeh',
        'Holiday',
        'Music',
        'Nature',
        'Other',
        'Scenery',
        'Seasonal',
        'Solid',
        'Sports',
        'Websites',
    ])
)
@pytest.mark.nondestructive
def test_themes_categories(base_url, selenium, count, category):
    themes = Themes(selenium, base_url).open()
    # clicking through each Theme Category
    themes.categories.category_list[count].click()
    category_results = Search(selenium, base_url)
    # checking that search results within that category are sorted correctly
    category_results.wait_for_contextcard_update(category)
    assert 'sort=recommended%2Cusers' in selenium.current_url
    select = Select(category_results.filter_by_sort)
    assert 'Most Users' in select.first_selected_option.text
