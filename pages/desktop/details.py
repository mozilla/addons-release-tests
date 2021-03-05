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
        return self.find_element(*self._install_button_state_locator).\
            get_attribute('disabled')

    @property
    def contribute(self):
        return self.Contribute(self)

    @property
    def permissions(self):
        return self.Permissions(self)

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

    class Permissions(Region):
        _permissions_header_locator = (By.CSS_SELECTOR, '.PermissionsCard header')
        _permissions_list_locator = (By.CSS_SELECTOR, '.PermissionsCard-list--required li')
        _permissions_learn_more_locator = (By.CLASS_NAME, 'PermissionCard-learn-more')

        @property
        def permissions_card_header(self):
            return self.find_element(*self._permissions_header_locator).text

        @property
        def permissions_list(self):
            items = self.find_elements(*self._permissions_list_locator)
            return [self.PermissionDetails(self.page, el) for el in items]

        def click_permissions_button(self):
            self.find_element(*self._permissions_learn_more_locator).click()
            self.wait.until(expected.number_of_windows_to_be(2))
            new_tab = self.selenium.window_handles[1]
            self.selenium.switch_to_window(new_tab)

        class PermissionDetails(Region):
            _permission_icon_locator = (By.CSS_SELECTOR, '.Permission .Icon')
            _permission_description_locator = (By.CLASS_NAME, 'Permission-description')

            @property
            def permission_icon(self):
                return self.find_element(*self._permission_icon_locator)

            @property
            def permission_description(self):
                return self.find_element(*self._permission_description_locator)
