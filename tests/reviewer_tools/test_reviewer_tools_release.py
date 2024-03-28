import pytest

from pages.desktop.reviewer_tools.reviewer_tools_homepage import ReviewerToolsHomepage
from pages.desktop.reviewer_tools.addon_review_page import ReviewAddonPage
from scripts import reusables
from pages.desktop.developers.devhub_home import DevHubHome
from selenium.webdriver.support import expected_conditions as EC

def submit_addon_method(selenium, base_url):
    devhub_page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    submit_addon = devhub_page.click_submit_addon_button()
    submit_addon.select_listed_option()
    submit_addon.click_continue()
    submit_addon.upload_addon("listed-addon.zip")
    submit_addon.is_validation_successful()
    assert submit_addon.success_validation_message.is_displayed()
    source = submit_addon.click_continue_upload_button()
    source.select_no_to_omit_source()
    confirmation_page = source.continue_listed_submission()
    random_string = reusables.get_random_string(10)
    summary = reusables.get_random_string(10)
    confirmation_page.set_addon_name(random_string)
    confirmation_page.set_addon_summary(summary)
    confirmation_page.select_categories(1)
    confirmation_page.select_license_options[0].click()
    confirmation_page.submit_addon()
    return f"listed-addon{random_string}"

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
@pytest.mark.failing
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
            "Updates" in themes_updates_page.themes_updates_selected.text
    )
    themes_updates_page.assert_queue_viewing_themes_updates()


@pytest.mark.login("reviewer_user")
def test_information_on_add_on_review_page_tc_id_C354060(selenium, base_url, variables):
    """Load AMO Reviewer Tools homepage."""
    addon_review_page = ReviewAddonPage(selenium, base_url)
    """Open an add-on review page"""
    selenium.get(f"{base_url}/{addon_review_page.URL_TEMPLATE}9609")
    addon_review_page.wait_for_page_to_load()
    """Assert that the Addon Review Page has the following elements:"""
    """Announcement
        - the announcement text box can be dismissed by clicking on the X button in top right corner
        - a text box on top of the review page where admin reviewers can communicate messages to other reviewers"""
    addon_review_page.assert_announcement_section_displayed()
    """Add-on information Section"""
    addon_review_page.assert_addon_info_section_displayed()
    """Sidenav"""
    addon_review_page.assert_sidenav_section_displayed()
    """Abuse Reports"""
    addon_review_page.assert_abuse_report_section_displayed()
    """Add-on History"""
    addon_review_page.assert_addon_history_section_displayed()
    """Reviewer actions"""
    addon_review_page.assert_reviewer_actions_section_displayed()
    """Whiteboards"""
    addon_review_page.assert_whiteboard_section_displayed()
    """More actions"""
    addon_review_page.assert_more_actions_section_displayed()


@pytest.mark.login("reviewer_user")
def test_logs_add_on_review_log_tc_id_C4588(selenium, base_url, variables):
    """Load AMO Reviewer Tools homepage."""
    reviewer_tools_homepage = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """AMO Reviewer Tools homepage is displayed without any layout issues."""
    reviewer_tools_homepage.assert_reviewer_tools_section()
    """Select "Add-on Review Log" from the available options."""
    manual_review_log_page = reviewer_tools_homepage.click_manual_review_log_link()
    """Add-on Review Log page is loaded
    Should contain the following:
    - URL is https://reviewers.addons.allizom.org/en-US/reviewers/reviewlog
    - Filter section where user is able to chose between which dates to view entries for and a type. 
    There is a "Filter" button colored in blue
    - A list of reviewed add-ons containing the following information: Date, Event, Editor and a Show Comments link. 
    When the Show Comments link is clicked, a list of comments is displayed under the add-on in the list.
    Note: If there are no reviews for the selected period, 
    the following message is displayed "No reviews found for this period."""
    EC.url_contains(manual_review_log_page.URL_TEMPLATE)
    manual_review_log_page.assert_review_page_elements()
    manual_review_log_page.assert_no_results_search(variables["reviewer_tools_no_results_in_this_period_message"])


@pytest.mark.login("reviewer_user")
def test_logs_moderated_review_log_tc_id_C4614(selenium, base_url, variables):
    """Load AMO Reviewer Tools homepage"""
    reviewer_tools_homepage = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """AMO Reviewer Tools homepage is displayed without any layout issues"""
    reviewer_tools_homepage.assert_reviewer_tools_section()
    """Go to User Ratings Moderation queue and select Moderated Review Log from the available options."""
    moderated_review_log_page = reviewer_tools_homepage.click_moderated_review_log_link()
    """Add-on Moderated Review Log page is loaded - https://reviewers.addons.allizom.org/en-US/reviewers/logs
    Please verify the the following:   
    a) Filter section where user is able to chose between which dates to view entries for and a "Filter by type/action" containing a dropdown list with "Approved Reviews/Deleted Reviews" options. There is a "Filter" button colored in blue.  
    b) A list of reviewed add-ons containing the following information: Date, Event (Editor, Review, name of the Add-on and More Details links)  
    c) If "More Details" link is clicked, "Log Details" page is loaded containing details about the Add-on/Review  
    Note: If there are no moderated reviews for the selected period, the following message is displayed "No events found for this period."""
    moderated_review_log_page.assert_moderated_review_log_page_elements()
    log_details_page = moderated_review_log_page.click_more_details_link()
    log_details_page.assert_log_details_section_elements()


@pytest.mark.login("reviewer_user")
def test_reviewer_tools_review_guide_for_each_queue_page_C104890(selenium, base_url, variables):
    """Load AMO Reviewer Tools homepage"""
    reviewer_tools_homepage = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """AMO Reviewer Tools homepage is displayed without any layout issues"""
    reviewer_tools_homepage.assert_reviewer_tools_section()
    """Click on the Review Guide link available in the following queues and verify that it redirects accordingly:"""
    """Manual Review Add-ons"""
    """The review guide for the corresponding queues redirects as follows:
    Manual Review Add-ons - Review Guide -->https://wiki.mozilla.org/Add-ons/Reviewers/Guide"""
    reviewer_tools_homepage.click_addon_review_guide_link()
    EC.url_contains("/Add-ons/Reviewers/Guide")
    reviewer_tools_homepage.open().wait_for_page_to_load()
    """Themes"""
    """Static Themes - Review Guide -->https://wiki.mozilla.org/Add-ons/Reviewers/Themes/Guidelines"""
    reviewer_tools_homepage.click_themes_review_guide_click()
    EC.url_contains("/Add-ons/Reviewers/Themes/Guidelines")
    reviewer_tools_homepage.open().wait_for_page_to_load()
    """User Ratings Moderation"""
    """User Ratings Moderation - Review Guide -->https://wiki.mozilla.org/Add-ons/Reviewers/Guide/Moderation"""
    reviewer_tools_homepage.click_moderation_guide_click()
    EC.url_contains("/Add-ons/Reviewers/Guide/Moderation")


@pytest.mark.login("reviewer_user")
def test_queues_ratings_awaiting_moderation_tc_id_C4586(selenium, base_url):
    """Load AMO Reviewer Tools homepage"""
    reviewer_tools_homepage = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """AMO Reviewer Tools homepage is displayed without any layout issues"""
    reviewer_tools_homepage.assert_reviewer_tools_section()
    """Go to "User Ratings Moderation" queues  and select "Ratings Awaiting Moderation" from the available options"""
    ratings_awaiting_moderation = reviewer_tools_homepage.click_ratings_awaiting_moderation()
    """Moderated reviews Queues page is displayed - https://reviewers.addons.allizom.org/en-US/reviewers/queue/reviews
    Please verify if :    
    a) A multitab containing all queue types is displayed and "Moderated Reviews" is selected  
    b) A list of moderated reviews is displayed containing the app name, rating and author, the reason for moderation   
    c) Moderation actions on the right side : "Keep review; remove flags", "Skip for now" and "Delete review"  
    d) A "Process reviews" blue button (at the beginning and on the end of the reviews table)"""
    ratings_awaiting_moderation.assert_moderation_actions_section_elements()
    ratings_awaiting_moderation.assert_process_reviews_buttons()

@pytest.mark.login("reviewer_user")
def test_content_approve_version_tc_id_T5456486(selenium, base_url):
    """Submit a new add-on in order to test the content approve function"""
    addon_slug = submit_addon_method(selenium, base_url)
    """Load AMO Reviewer Tools homepage"""
    reviewer_tools_homepage = ReviewerToolsHomepage(selenium, base_url).open().wait_for_page_to_load()
    """AMO Reviewer Tools homepage is displayed without any layout issues"""
    reviewer_tools_homepage.assert_reviewer_tools_section()
    """Go to "User Ratings Moderation" queues  and select "Content Review" from the available options"""
    content_review_page = reviewer_tools_homepage.click_content_review_link()
    content_review_page.assert_queue_viewing_content_review()
