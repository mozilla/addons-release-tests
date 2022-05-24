import time

import pytest
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

    def wait_for_version_autoapproval(self, value):
        """Method that verifies if auto-approval occurs within a set time"""
        timeout_start = time.time()
        # auto-approvals should normally take ~5 minutes;
        # set a loop to verify if approval occurs within this interval
        while time.time() < timeout_start + 300:
            # refresh the page to check if the status has changed
            self.selenium.refresh()
            if value not in self.version_approval_status.text:
                # wait 30 seconds before we refresh again
                time.sleep(30)
            # break the loop of the status changed to the expected value within set time
            else:
                break
        # if auto-approval took longer than normal, we want to fail the test and capture the final status
        else:
            pytest.fail(
                f'Autoapproval took longer than normal; '
                f'Addon final status was "{self.version_approval_status.text}" instead of "{value}"'
            )

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
