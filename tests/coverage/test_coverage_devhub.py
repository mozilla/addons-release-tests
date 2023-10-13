import pytest

from pages.desktop.developers.edit_theme import EditTheme


@pytest.mark.coverage
@pytest.mark.login("developer")
def test_upload_4mb_screenshots(base_url, selenium, variables, wait):
    edit_product_page = EditTheme(selenium, base_url).open_edit_page(variables["4mb_theme_slug"], base_url, selenium)
