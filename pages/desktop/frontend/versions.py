from pypom import Region
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected

from pages.desktop.base import Base
from regions.desktop.rating_stats_card import RatingStats


class Versions(Base):
    _versions_page_header_locator = (By.CSS_SELECTOR, '.AddonVersions-versions header')
    _latest_version_locator = (By.CSS_SELECTOR, '.Card-contents li:nth-child(2) h2')
    _versions_list_locator = (By.CSS_SELECTOR, '.AddonVersionCard')
    _notice_message_locator = (
        By.CSS_SELECTOR,
        '.Card-contents .Notice-warning .Notice-text',
    )
    _notice_message_text_locator = (By.CSS_SELECTOR, '.AddonVersions-warning-text')
    _rating_card_locator = (By.CSS_SELECTOR, '.AddonSummaryCard')

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            expected.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText'))
        )
        return self

    @property
    def versions_page_header(self):
        return self.find_element(*self._versions_page_header_locator)

    @property
    def latest_version_number(self):
        el = self.find_element(*self._latest_version_locator).text
        return el.split()[1].replace('Version ', '')

    @property
    def notice_message(self):
        return self.find_element(*self._notice_message_locator)

    @property
    def rating_card(self):
        el = self.find_element(By.CLASS_NAME, 'AddonSummaryCard')
        return RatingStats(self, el)

    @property
    def latest_version(self):
        return self.VersionCard(
            self, self.find_elements(*self._versions_list_locator)[0]
        )

    @property
    def versions_list(self):
        items = self.find_elements(*self._versions_list_locator)
        return [self.VersionCard(self, el) for el in items]

    class VersionCard(Region):
        _version_number_locator = (By.CSS_SELECTOR, '.AddonVersionCard-version')
        _released_date_locator = (By.CSS_SELECTOR, '.AddonVersionCard-fileInfo')
        _version_release_notes_locator = (
            By.CSS_SELECTOR,
            '.AddonVersionCard-releaseNotes',
        )
        _license_link_locator = (By.CSS_SELECTOR, '.AddonVersionCard-license > a')
        _license_text_locator = (By.CSS_SELECTOR, '.AddonVersionCard-license')
        _warning_message_locator = (By.CSS_SELECTOR, '.Notice-text')
        _warning_learn_more_button_locator = (By.CSS_SELECTOR, '.Notice-button')
        _add_to_firefox_button_locator = (By.CSS_SELECTOR, '.AMInstallButton-button')
        _download_link_locator = (
            By.CSS_SELECTOR,
            '.InstallButtonWrapper-download-link',
        )

        @property
        def version_number(self):
            return self.find_element(*self._version_number_locator).text.split()[1]

        @property
        def released_date(self):
            text = self.find_element(*self._released_date_locator).text
            text = text.split('Released ')[1]
            text = text.split('-')[0][:-1]
            return text

        @property
        def version_size(self):  # memory size, ex: 7.35 KB
            return self.find_element(*self._released_date_locator).text.split('-')[1][
                1:
            ]

        @property
        def version_release_notes(self):
            return self.find_element(*self._version_release_notes_locator)

        @property
        def license_link(self):
            return self.find_element(*self._license_link_locator)

        @property
        def license_text(self):
            text = self.find_element(*self._license_text_locator).text
            if self.license_link:
                text += self.license_link.get_attribute('href')
            return text

        @property
        def warning_message(self):
            return self.find_element(*self._warning_message_locator)

        @property
        def warning_learn_more_button(self):
            return self.find_element(*self._warning_learn_more_button_locator)

        @property
        def add_to_firefox_button(self):
            return self.find_element(*self._add_to_firefox_button_locator)

        @property
        def download_link(self):
            return self.find_element(*self._download_link_locator)
