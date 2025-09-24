import time

from pypom import Region

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base
from pages.desktop.developers.edit_addon import EditAddon


class ManageAddons(Base):
    _my_addons_page_logo = (By.CSS_SELECTOR, ".site-titles")
    _page_title_locator = (By.CSS_SELECTOR, ".hero > h1")
    _my_themes_section_button_locator = (
        By.CSS_SELECTOR,
        ".submission-type-tabs > a:nth-child(2)",
    )
    _sort_by_created_locator = (By.LINK_TEXT, "Created")
    _addon_items_locator = (By.CLASS_NAME, "item.addon")
    _submit_addon_button_locator = (By.CSS_SELECTOR, "#submit-addon > a")

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(self._submit_addon_button_locator)
        )
        return self

    @property
    def my_addons_page_logo(self):
        self.wait_for_element_to_be_displayed(self._my_addons_page_logo)
        return self.find_element(*self._my_addons_page_logo)

    @property
    def my_addons_page_title(self):
        self.wait_for_element_to_be_displayed(self._page_title_locator)
        return self.find_element(*self._page_title_locator)

    def click_on_my_themes(self):
        self.find_element(*self._my_themes_section_button_locator).click()
        self.wait.until(
            lambda _: self.find_element(
                *self._my_themes_section_button_locator
            ).get_attribute("class")
            == "active"
        )

    def sort_by_created(self):
        self.find_element(*self._sort_by_created_locator).click()

    @property
    def addon_list(self):
        items = self.find_elements(*self._addon_items_locator)
        return [self.AddonDetails(self, el) for el in items]

    class AddonDetails(Region):
        _addon_name_locator = (By.CSS_SELECTOR, ".item.addon .info > h3")
        _addon_edit_link_locator = (By.CSS_SELECTOR, ".item.addon .info > h3 > a")

        @property
        def name(self):
            self.wait.until(EC.visibility_of_element_located(self._addon_name_locator))
            return self.find_element(*self._addon_name_locator).text

        def click_addon_name(self):
            time.sleep(5)
            self.find_element(*self._addon_edit_link_locator).click()
            time.sleep(5)
            return EditAddon(self.driver, self.page.base_url).wait_for_page_to_load()
