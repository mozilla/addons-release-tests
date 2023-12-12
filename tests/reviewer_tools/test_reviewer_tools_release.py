import pytest

from pages.desktop.reviewer_tools.reviewer_tools_homepage import ReviewerToolsHomepage
from pages.desktop.developers.devhub_home import DevHubHome


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
def test_queues_manual_review_queue_tc_id_c4583(selenium, base_url):
    DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    """Load AMO Reviewer Tools homepage."""
    """AMO Reviewer Tools homepage is displayed without any layout issues."""
    reviewer_tools_page = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """Go to **Manual Review** and select **Manual Review** from the available options."""
    manual_review_page = reviewer_tools_page.click_manual_review_link()
    """The queue is displayed - https://reviewers.addons.allizom.org/en-US/reviewers/queue/extension 
    There's a tabnav containing all queues corresponding to your reviewer permissions is displayed 
    and **Manual Review** is selected"""
    manual_review_page.assert_tab_viewing()
    """Under the selected tab there is a list of add-ons with various information: 
    "Add-on ", "Type", "Due Date", "Flags", "Maliciousness Score" """
    manual_review_page.assert_queue_viewing()
