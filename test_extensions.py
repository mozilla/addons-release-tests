import pytest

from pages.desktop.extensions import Extensions
from pages.desktop.home import Home


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_category_section_loads_correct_category(base_url, selenium):
    page = Extensions(selenium, base_url).open()
    item = page.categories.category_list[0]
    name = item.name
    category = item.click()
    assert name in category.header.name
