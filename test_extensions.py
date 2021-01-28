import pytest
from pages.desktop.extensions import Extensions
from pages.desktop.search import Search
from selenium.webdriver.support.select import Select


@pytest.mark.desktop_only
@pytest.mark.parametrize(
    'count, category',
    enumerate([
        'Alerts & Updates',
        'Appearance',
        'Bookmarks',
        'Download Management',
        'Feeds, News & Blogging',
        'Games & Entertainment',
        'Language Support',
        'Other',
        'Photos, Music & Videos',
        'Privacy & Security',
        'Search Tools',
        'Shopping',
        'Social & Communication',
        'Tabs',
        'Web Development',
    ])
)
@pytest.mark.nondestructive
def test_extensions_categories(base_url, selenium, count, category):
    extensions = Extensions(selenium, base_url).open()
    # clicking through each Category listed on Extensions homepage
    extensions.categories.category_list[count].click()
    category_results = Search(selenium, base_url)
    # checking that category search results are loaded and sorted by users
    category_results.wait_for_contextcard_update(category)
    assert 'sort=recommended%2Cusers' in selenium.current_url
    select = Select(category_results.filter_by_sort)
    assert 'Most Users' in select.first_selected_option.text
