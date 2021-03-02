from pypom import Region

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected

from pages.desktop.base import Base


class Detail(Base):
    _root_locator = (By.CLASS_NAME, 'Addon-extension')
    _addon_name_locator = (By.CLASS_NAME, 'AddonTitle')
    _compatible_locator = (By.CSS_SELECTOR, '.AddonCompatibilityError')
    _install_button_locator = (By.CLASS_NAME, 'AMInstallButton-button')
    _install_button_state_locator = (By.CSS_SELECTOR, '.AMInstallButton a')

    def wait_for_page_to_load(self):
        self.wait.until(
            expected.invisibility_of_element_located(
                (By.CLASS_NAME, 'LoadingText')))
        return self

    @property
    def name(self):
        return self.find_element(*self._addon_name_locator).text

    @property
    def is_compatible(self):
        return not self.is_element_displayed(*self._compatible_locator)

    @property
    def incompatibility_message(self):
        return self.find_element(*self._compatible_locator).text

    def install(self):
        self.find_element(*self._install_button_locator).click()

    @property
    def button_text(self):
        self.wait.until(expected.invisibility_of_element_located(
            (By.CLASS_NAME, 'AMInstallButton-loading-button')))
        return self.find_element(*self._install_button_locator).text

    @property
    def button_state_disabled(self):
        # checking that an inactive install button has a 'disabled' attribute
        return self.find_element(*self._install_button_state_locator). \
            get_attribute('disabled')

    @property
    def contribute(self):
        return self.Contribute(self)

    class Contribute(Region):
        _contribute_header_locator = (By.CSS_SELECTOR, '.ContributeCard header')
        _contribute_content_locator = (By.CLASS_NAME, 'ContributeCard-content')
        _contribute_button_locator = (By.CLASS_NAME, 'ContributeCard-button')

        @property
        def contribute_card_header(self):
            return self.find_element(*self._contribute_header_locator).text

        @property
        def contribute_card_content(self):
            return self.find_element(*self._contribute_content_locator).text

        def click_contribute_button(self):
            self.find_element(*self._contribute_button_locator).click()
            self.wait.until(expected.number_of_windows_to_be(2))
            new_tab = self.selenium.window_handles[1]
            self.selenium.switch_to_window(new_tab)
