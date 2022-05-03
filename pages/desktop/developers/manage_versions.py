from pypom import Region, Page

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ManageVersions(Page):
    _version_list_locator = (By.ID, 'version-list')
    _version_approval_status_locator = (
        By.CSS_SELECTOR,
        '#version-list .file-status div:nth-child(1)',
    )
    _delete_addon_button_locator = (By.CLASS_NAME, 'delete-button.delete-addon')

    def wait_for_page_to_load(self):
        self.wait.until(EC.visibility_of_element_located(self._version_list_locator))
        return self

    @property
    def version_approval_status(self):
        return self.find_element(*self._version_approval_status_locator)

    def delete_addon(self):
        self.find_element(*self._delete_addon_button_locator).click()
        return self.DeleteAddonModal(self).wait_for_region_to_load()

    class DeleteAddonModal(Region):
        _root_locator = (By.ID, 'modal-delete')
        _delete_confirmation_string_locator = (
            By.CSS_SELECTOR,
            'p:nth-of-type(2) > label',
        )
        _delete_confirmation_text_input_locator = (
            By.CSS_SELECTOR,
            'input[name="slug"]',
        )
        _delete_button_locator = (By.CSS_SELECTOR, '.delete-button')

        def wait_for_region_to_load(self):
            self.wait.until(EC.visibility_of_element_located(self._root_locator))
            return self

        @property
        def delete_confirmation_string(self):
            """This is the addon slug which is required to confirm deleting an addon"""
            return self.find_element(
                *self._delete_confirmation_string_locator
            ).text.split()[-1]

        def input_delete_confirmation_string(self):
            self.find_element(*self._delete_confirmation_text_input_locator).send_keys(
                self.delete_confirmation_string
            )

        def confirm_delete_addon(self):
            self.find_element(*self._delete_button_locator).click()
            from pages.desktop.developers.addons_manage import ManageAddons

            return ManageAddons(
                self.selenium, self.page.base_url
            ).wait_for_page_to_load()
