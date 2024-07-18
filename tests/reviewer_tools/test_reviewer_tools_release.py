import pytest

from pages.desktop.reviewer_tools.reviewer_tools_homepage import ReviewerToolsHomepage
from pages.desktop.developers.devhub_home import DevHubHome
from selenium.webdriver.support import expected_conditions as EC

""""""
@pytest.mark.login("reviewer_user")
def test_reviewer_tools_homepage_layout_tc_id_c4589(selenium, base_url):
    """Log into AMO homepage and select 'Reviewer Tools' from the user menu"""
    """Reviewers dashboard loads without layout issues at https://reviewers.addons.allizom.org/en-US/reviewers/"""
    """Check the components of the reviewer dashboard"""
    """Reviewers homepage contains the following:  
    a) Reviewer Tools title on the header"""
    reviewer_tools_page = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """
    b) Username, Tools, Other Applications menus"""
    assert (
        reviewer_tools_page.tools_header.is_displayed(),
        reviewer_tools_page.user_header.is_displayed()
    )
    """
    c) Announcement section (message is displayed to each reviewer permission) """
    assert (
        reviewer_tools_page.announcement_section.is_displayed()
    )
    """
    d) Various queues:  
        1. **Manual Review:** - Manual Review Queue, Review Log, Review Guide
        2. **Human Review Needed:** - Flagged by MAD for Human Review
        3. **Content Review:** - Content Review
        4. **Themes:** - New (<number>), Updates (<number>), Review Log, Review Guide
        5. **Admin Tools:** - Add-ons Pending Rejection (Admin Reviewers only)"""
    reviewer_tools_page.assert_reviewer_tools_section()
    """
    e) Page Footer"""
    assert (
        reviewer_tools_page.mozilla_logo.is_displayed()
    )


@pytest.mark.login("reviewer_user")
def test_queues_manual_review_queue_tc_id_c4583(selenium, base_url, wait):
    """Load AMO Reviewer Tools homepage."""
    """AMO Reviewer Tools homepage is displayed without any layout issues."""
    reviewer_tools_page = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """Go to **Manual Review** and select **Manual Review** from the available options."""
    manual_review_page = reviewer_tools_page.click_manual_review_link()
    """The queue is displayed - https://reviewers.addons.allizom.org/en-US/reviewers/queue/extension 
    There's a tabnav containing all queues corresponding to your reviewer permissions is displayed 
    and **Manual Review** is selected"""
    assert (
        EC.url_contains("reviewers/queue/extension")
    )
    reviewer_tools_page.assert_tab_viewing()
    """Under the selected tab there is a list of add-ons with various information: 
    "Add-on ", "Type", "Due Date", "Flags", "Maliciousness Score" """
    manual_review_page.assert_queue_viewing_manual_review()


@pytest.mark.login("reviewer_user")
def test_queues_content_review_tc_id_c79313(selenium, base_url, wait):
    """Load AMO Reviewer Tools homepage."""
    """AMO Reviewer Tools homepage is displayed without any layout issues."""
    reviewer_tools_page = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """Go to "Content Review queue " and select "Content Review" from the available options."""
    content_review_page = reviewer_tools_page.click_content_review_link()
    """Content Review queue is loaded - https://reviewers.addons.allizom.org/en-US/reviewers/queue/content_review."""
    """Please verify the following content:"""
    """a)A table containing the following:
                - Add-on name column
                - Flags - add-on type or flags
                - Last content review - time from last content review"""
    content_review_page.assert_queue_viewing_content_review()
    assert (
        EC.url_contains("reviewers/queue/content_review")
    )
    """b)Announcement - displays the message of the day"""
    assert (
        reviewer_tools_page.announcement_section.is_displayed()
    )
    """c)A multitab containing several queue types is displayed and "Content Review" is selected"""
    reviewer_tools_page.assert_tab_viewing()


@pytest.mark.login("reviewer_user")
def test_queues_themes_new_tc_id_c325790(selenium, base_url):
    """Load AMO Reviewer Tools homepage."""
    """AMO Reviewer Tools homepage is displayed without any layout issues."""
    reviewer_tools_page = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """Go to Themes queue and select "New" from the available options."""
    themes_new_page = reviewer_tools_page.click_themes_new_link()
    """The list of themes pending for review is displayed - https://reviewers.addons-dev.allizom.org/en-US/reviewers/queue/theme_new
    Please verify if :  
    b) A tab nav containing all queues corresponding to your reviewer permissions is displayed and "New" """
    reviewer_tools_page.assert_tab_viewing()
    assert (
        EC.url_contains("reviewers/queue/theme_new")
    )
    """d) Under the selected tab there is a list of add-ons with various information: "Add-on ", "Type", "Waiting time", "Flags"
       e) The pending list contains only static themes"""
    assert (
        reviewer_tools_page.announcement_section.is_displayed()
    )
    themes_new_page.assert_queue_viewing_themes_new()

@pytest.mark.login("reviewer_user")
def test_queues_themes_updates_tc_id_c325792(selenium, base_url):
    """Load AMO Reviewer Tools homepage."""
    """AMO Reviewer Tools homepage is displayed without any layout issues."""
    reviewer_tools_page = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """Go to Themes queue " and select "Updates" from the available options"""
    themes_updates_page = reviewer_tools_page.click_themes_updates_link()
    """A list of add-on versions pending for review is displayed - https://reviewers.addons-dev.allizom.org/en-US/reviewers/queue/theme_updates
    Please verify if :   
    a) A tabnav containing all queues corresponding to your reviewer permissions is displayed and "Updates" 
    (with the identifiable "themes" icon) is selected"""
    reviewer_tools_page.assert_tab_viewing()
    """b) Under the selected tab there is a list of add-ons with various information: "Add-on ", "Type", 
    "Waiting time", "Flags"""
    assert (
        EC.url_contains("reviewers/queue/theme_updates")
    )
    assert (
        "Updates" in themes_updates_page.themes_selected.text
    )
    themes_updates_page.assert_queue_viewing_themes_new()
