from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base
from pages.desktop.frontend.details import Detail


class StaticPages(Base):
    """This class will store informative pages, such as 404 pages, server error pages
    and other pages that have only an informative scope"""

    _not_found_page_locator = (By.CSS_SELECTOR, ".NotFound")
    _notice_text_locator = (By.CSS_SELECTOR, ".Notice-warning")
    _page_header_locator = (By.CSS_SELECTOR, ".Card-header-text")
    _content_locator = (By.CSS_SELECTOR, ".Card-contents")
    _content_card_links_locator = (By.CSS_SELECTOR, ".Card-contents a")
    # ------- Review Guidelines page
    _review_guidelines_page_forum_link_locator = (By.CSS_SELECTOR, "section > p > a")
    # ------- About Firefox Add-ons page
    _thunderbird_link_locator = (By.CSS_SELECTOR, "#about > p > a:nth-child(1)")
    _seamonkey_link_locator = (By.CSS_SELECTOR, "#about > p > a:nth-child(2)")
    _get_involved_links_locator = (
        By.CSS_SELECTOR,
        ".Card-contents section > ul > li > a",
    )
    # ------- Blocked Add-on page
    _blocked_addon_page_links_locator = (By.CSS_SELECTOR, ".Card-contents > p > a")
    # ------- Login Expired page
    _reload_the_page_link_locator = (By.CSS_SELECTOR, ".ReloadPageLink")

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "LoadingText")),
            message="The requested page could not be loaded",
        )
        return self

    @property
    def not_found_page(self):
        self.wait.until(EC.visibility_of_element_located(self._not_found_page_locator))
        return self.find_element(*self._not_found_page_locator)

    @property
    def notice_messages(self):
        self.wait.until(EC.visibility_of_element_located(self._notice_text_locator))
        return self.find_elements(*self._notice_text_locator)

    @property
    def page_header(self):
        self.wait.until(EC.visibility_of_element_located(self._page_header_locator))
        return self.find_element(*self._page_header_locator).text

    @property
    def content(self):
        self.wait.until(EC.visibility_of_element_located(self._content_locator))
        return self.find_element(*self._content_locator)

    # ------- Review Guidelines page
    @property
    def forum_link(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._review_guidelines_page_forum_link_locator
            )
        )
        return self.find_element(*self._review_guidelines_page_forum_link_locator)

    # ------- About Firefox Add-ons page
    @property
    def page_links(self):
        self.wait.until(
            EC.visibility_of_element_located(self._content_card_links_locator)
        )
        return self.find_elements(*self._content_card_links_locator)

    @property
    def thunderbird_link(self):
        self.wait.until(
            EC.visibility_of_element_located(self._thunderbird_link_locator)
        )
        return self.find_element(*self._thunderbird_link_locator)

    @property
    def seamonkey_link(self):
        self.wait.until(EC.visibility_of_element_located(self._seamonkey_link_locator))
        return self.find_element(*self._seamonkey_link_locator)

    @property
    def get_involved_links(self):
        # add all the links except 'wiki'
        self.wait.until(
            EC.visibility_of_element_located(self._get_involved_links_locator)
        )
        links = self.find_elements(*self._get_involved_links_locator)
        # add the 'wiki' link
        links.append(self.find_elements(*self._content_card_links_locator)[10])
        return links

    @property
    def report_an_issue_links(self):
        self.wait.until(
            EC.visibility_of_element_located(self._content_card_links_locator)
        )
        return self.find_elements(*self._content_card_links_locator)[11:15]

    @property
    def get_support_links(self):
        self.wait.until(
            EC.visibility_of_element_located(self._content_card_links_locator)
        )
        return self.find_elements(*self._content_card_links_locator)[15:]

    # ------- Blocked Add-on page
    @property
    def addon_policies_link(self):
        self.wait.until(
            EC.visibility_of_element_located(self._blocked_addon_page_links_locator)
        )
        return self.find_elements(*self._blocked_addon_page_links_locator)[0]

    @property
    def certain_criteria_link(self):
        self.wait.until(
            EC.visibility_of_element_located(self._blocked_addon_page_links_locator)
        )
        return self.find_elements(*self._blocked_addon_page_links_locator)[1]

    @property
    def this_support_article_link(self):
        self.wait.until(
            EC.visibility_of_element_located(self._blocked_addon_page_links_locator)
        )
        return self.find_elements(*self._blocked_addon_page_links_locator)[2]

    # ------- Login Expired page
    @property
    def logged_out_notice_message(self):
        self.wait.until(
            EC.visibility_of_element_located(self._logged_out_notice_locator)
        )
        return self.find_element(*self._logged_out_notice_locator)

    @property
    def click_reload_page_link(self):
        self.wait.until(EC.element_to_be_clickable(self._reload_the_page_link_locator))
        self.find_element(*self._reload_the_page_link_locator).click()
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".AddonTitle"))
        )
        return Detail(self.driver, self.base_url)
