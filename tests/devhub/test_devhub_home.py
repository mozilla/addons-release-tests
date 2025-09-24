"""test_devhub_home.py focuses on the homepage from devhub"""
import pytest
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.developers.devhub_home import DevHubHome
from scripts import reusables



@pytest.mark.nondestructive
def test_devhub_logo(selenium, base_url):
    """Verifies that clicking on the DevHub homepage logo reloads
    the page and ensures that the logo remains displayed after the reload."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # clicks on the page logo and verifies page is reloaded
    page.page_logo.click()
    assert page.page_logo.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_click_extension_workshop(selenium, base_url):
    """Ensures that clicking on the "Extension Workshop" link in the
    DevHub header menu redirects the user to the Extension Workshop
    page and verifies that the page loads correctly."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # clicks on EW in the header menu and checks page is loaded
    page.extension_workshop.click()
    page.extension_workshop_is_loaded()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_click_documentation(selenium, base_url):
    """Verifies that clicking on the "Documentation" link in the
    DevHub header menu redirects the user to the Documentation
    page and confirms the page loads properly."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # clicks on Documentation header menu and checks page is loaded
    page.click_documentation()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_click_support(selenium, base_url):
    """Verifies that clicking on the "Support" link
    in the DevHub header menu redirects to the
    "Add-ons#Get_in_touch" section and the URL changes correctly."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # clicks on Support header menu and checks page is loaded
    page.click_support()
    page.wait_for_current_url("Add-ons#Get_in_touch")


@pytest.mark.nondestructive
def test_click_blog(selenium, base_url):
    """Ensures that clicking on the "Blog" link in the
    DevHub header menu takes the user to the Blog section
    of the site and verifies the page loads correctly."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # clicks on Blog header menu and checks page is loaded
    page.click_blog()


@pytest.mark.sanity
@pytest.mark.nondestructive
@pytest.mark.login("developer")
def test_devhub_login(selenium, base_url, wait):
    """Verifies the login process for a developer.
    After logging in, it checks that the user avatar
    is displayed, confirming a successful login."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # verifies that the user has been logged in by looking at the user icon
    wait.until(lambda _: page.user_avatar.is_displayed())


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_devhub_page_overview(selenium, base_url, variables):
    """Verifies the content in the
    "Overview" section on the DevHub homepage,
    including the header and summary.
    It also checks that the "Learn How" button
    redirects to the Extension Workshop page."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # checks the content in the page 'Overview' - main section
    assert variables["devhub_overview_header"] in page.devhub_overview_title
    assert variables["devhub_overview_summary"] in page.devhub_overview_summary
    page.click_overview_learn_how_button()
    # checks that the link redirects to the extension workshop
    page.extension_workshop_is_loaded()

@pytest.mark.skip
@pytest.mark.nondestructive
def test_devhub_page_get_involved(selenium, base_url, variables, wait):
    """Tests the "Get Involved" section on the DevHub homepage,
    verifying the header, summary, image, and that the
    link redirects to the Add-ons/Contribute page."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # checks the content in the page 'Get Involved' - secondary section
    assert variables["devhub_get_involved_header"] in page.devhub_get_involved_title
    assert variables["devhub_get_involved_summary"] in page.devhub_get_involved_summary
    assert page.devhub_get_involved_image.is_displayed()
    page.devhub_get_involved_link.click()
    time.sleep(5)
    assert page.devhub_addon_contribute_title.text in "Add-ons/Contribute"

@pytest.mark.sanity
@pytest.mark.nondestructive
def test_devhub_get_involved_box(selenium, base_url, variables, wait):
    """Verifies the content of the "Get Involved" section
    on the DevHub homepage, checking the header,
    summary, and the display of an associated image."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # checks the content in the page 'Get Involved' - secondary section
    assert variables["devhub_get_involved_header"] in page.devhub_get_involved_title
    assert variables["devhub_get_involved_summary"] in page.devhub_get_involved_summary
    assert page.devhub_get_involved_image.is_displayed()

@pytest.mark.sanity
@pytest.mark.nondestructive
def test_devhub_page_content(selenium, base_url, variables):
    """Verifies the content in the "Content" section of
    the DevHub homepage, including the header, summary,
    and display of an image."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # checks the content in the page 'Content' - secondary section
    assert variables["devhub_content_header"] in page.devhub_content_title
    assert variables["devhub_content_summary"] in page.devhub_content_summary
    assert page.devhub_content_image.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_devhub_content_login_link(selenium, base_url, variables):
    """Ensures that clicking the login link in the
    "Content" section redirects to the FxA login page."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.click_content_login_link()
    # verify that the link opens the FxA login page
    page.wait_for_current_url(variables["fxa_login_page"])


@pytest.mark.nondestructive
@pytest.mark.login("developer")
def test_devhub_click_my_addons_header_link(selenium, base_url, wait):
    """Verifies that clicking the "My Add-ons" header link
    redirects the user to the "Manage Add-ons" page in
    DevHub and confirms the page loads correctly."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    my_addons_page = page.click_my_addons_header_link()
    # check that user is sent to the Manage addons page in devhub
    wait.until(
        lambda _: my_addons_page.my_addons_page_title.is_displayed(),
        message="My addons page title was not displayed",
    )


@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_devhub_click_header_profile_icon(selenium, base_url):
    """Verifies that clicking on the user profile
    icon in the DevHub header opens the user's profile page."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    user_profile = page.click_user_profile_picture()
    # verify that the user profile frontend page opens
    user_profile.wait_for_user_to_load()


@pytest.mark.nondestructive
def test_devhub_logged_in_page_hero_banner_tc_id_C15072(selenium, base_url, variables):
    """Verifies the content of the
    "logged-in" hero banner after logging in,
    ensuring the header and text are displayed correctly
    and that the Extension Workshop link works as expected."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login("regular_user")
    # verify the items present in the page logged in banner
    assert (
        variables["devhub_logged_in_banner_header"] in page.logged_in_hero_banner_header
    )
    assert variables["devhub_logged_in_banner_text"] in page.logged_in_hero_banner_text
    page.click_logged_in_hero_banner_extension_workshop_link()
    # verify that the Extension Workshop page is opened
    page.extension_workshop_is_loaded()


@pytest.mark.nondestructive
def test_devhub_my_addons_section_tc_id_C15072(selenium, base_url, variables):
    """Verifies the "My Add-ons" section after logging in,
    ensuring the correct header is displayed and that any
    relevant paragraphs about add-ons are visible."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login("regular_user")
    page.wait_for_page_to_load()
    assert "My Add-ons" in page.my_addons_section_header.text
    # if the current account has no add-ons submitted, this paragraph will be displayed
    assert (
        variables["devhub_my_addons_section_paragraph"]
        in page.my_addons_section_paragraph.text
    )


@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_devhub_my_addons_list_items(selenium, base_url, wait):
    """Verifies that the "My Add-ons"
    section displays up to 3 of the user's latest
    submitted add-ons, and ensures that each add-on
    has its icon, name, version, and rating (if available)."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # check that logged-in users can see up to 3 latest addons they've submitted
    assert len(page.my_addons_list) in range(1, 4)
    for addon in page.my_addons_list:
        # verify that each addon in the list has the following items
        assert addon.my_addon_icon.is_displayed()
        assert addon.my_addon_name.is_displayed()
        assert addon.my_addon_version_number.is_displayed()
        assert addon.my_addon_last_modified_date.is_displayed()
        # checks what we display if an addon was rated (rating stars) or not (placeholder text)
        try:
            assert "Not yet rated" in addon.my_addon_rating_text.text
        except AssertionError:
            assert "review" in addon.my_addon_rating_text.text
            assert addon.my_addon_rating_stars.is_displayed()


@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_devhub_my_addons_list_approval_status(selenium, base_url):
    """Verifies that each listed add-on has the current
    approval status displayed, especially for listed
    add-ons in the "My Add-ons" section."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    count = 0
    while count < len(page.my_addons_list):
        if page.my_addons_list[count].is_listed_addon():
            # if the add-on is listed, we check that the current status is displayed in DevHub homepage
            assert page.my_addons_list[count].my_addon_version_status.is_displayed()
        count += 1


@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_devhub_click_see_all_addons_link(selenium, base_url, wait):
    """Verifies that clicking the "See All Add-ons" link
    in the "My Add-ons" section correctly redirects
    the user to the Manage Add-ons page."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    my_addons_page = page.click_see_all_addons_link()
    wait.until(
        lambda _: my_addons_page.my_addons_page_title.is_displayed(),
        message="Manage addons page title was not displayed",
    )


@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_devhub_click_submit_new_addon_button_tc_id_c14882(selenium, base_url, wait):
    """Ensures that clicking the "Submit New Add-on" button
    redirects the user to the Add-on submission page
    and that the submission form header loads."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    distribution_page = page.click_submit_addon_button()
    wait.until(
        lambda _: distribution_page.submission_form_header.is_displayed(),
        message="The addon distribution page header was not displayed",
    )


@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_devhub_click_submit_new_theme_button(selenium, base_url, wait):
    """Verifies that clicking the "Submit New Theme" button
    redirects the user to the theme submission page
    and that the submission form header loads."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    distribution_page = page.click_submit_theme_button()
    wait.until(
        lambda _: distribution_page.submission_form_header.is_displayed(),
        message="The addon distribution page header as not displayed",
    )


@pytest.mark.nondestructive
def test_devhub_click_first_theme_button(selenium, base_url, variables):
    """Ensures that clicking the first "Theme" button
    shows the appropriate distribution agreement,
    either for add-ons or themes,
    based on the user's agreement status."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # an account with no add-ons submitted is used
    page.devhub_login("regular_user")
    page.wait_for_page_to_load()
    distribution_page = page.click_submit_theme_button()
    # if this user never accepted the distribution agreement, it should be displayed in the page, otherwise not
    try:
        assert (
            variables["devhub_submit_addon_agreement_header"]
            in distribution_page.submission_form_subheader.text
        )
    except AssertionError:
        assert (
            variables["devhub_submit_addon_distribution_header"]
            in distribution_page.submission_form_subheader.text
        )


@pytest.mark.nondestructive
def test_devhub_resources_footer_documentation_links_tc_id_C15072(selenium, base_url, variables):
    """Verifies that all "Documentation" links in the resources
    footer lead to the correct pages, confirming that
    the user is directed to the expected documentation sections."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login("regular_user")
    assert "Documentation" in page.resources.documentation_section_header
    count = 0
    # looping through the actual number of Documentation links present in the resources footer
    while count in range(len(page.resources.documentation_section_links)):
        link = page.resources.documentation_section_links[count]
        link.click()
        # checks that the expected page is opened when clicking on the link
        page.wait_for_current_url(variables["devhub_resources_doc_links"][count])
        # go back to devhub and select the next Documentation link
        selenium.back()
        count += 1


@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_devhub_resources_footer_tools_links_tc_id_C15072(selenium, base_url, variables):
    """Ensures that all "Tools" links in the resources
    footer lead to the correct pages, verifying that
    the user is taken to the correct tool-related sections."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    assert "Tools" in page.resources.tools_section_header
    count = 0
    # looping through the actual number of Tools links present in the resources footer
    while count in range(len(page.resources.tools_section_links) - 1):
        link = page.resources.tools_section_links[count]
        link.click()
        # checks that the expected page is opened when clicking on the link
        page.wait_for_current_url(variables["devhub_resources_tools_links"][count])
        # go back to devhub and select the next Tools link
        selenium.back()
        count += 1


@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_devhub_resources_footer_promote_links_tc_id_C15072(selenium, base_url, variables):
    """Verifies that the "Promote" links in the resources footer
    lead to the correct pages, confirming that users are directed
    to the appropriate promotion-related sections."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    assert "Promote" in page.resources.promote_section_header
    count = 0
    # looping through the actual number of Promote links present in the resources footer
    while count in range(len(page.resources.promote_section_links)):
        link = page.resources.promote_section_links[count]
        link.click()
        # checks that the expected page is opened when clicking on the link
        page.wait_for_current_url(variables["devhub_resources_promote_links"][count])
        # go back to devhub and select the next Promote link
        selenium.back()
        count += 1


@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_devhub_resources_join_addon_review(selenium, base_url, variables):
    """Verifies that the "Join Add-on Review" link in the resources section
    leads to the "Contribute/Code" section, allowing users
    to participate in reviewing add-ons."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    assert "Write Some Code" in page.resources.review_addons_section_header
    assert (
        variables["devhub_resources_review_addons_text"]
        in page.resources.review_addons_section_info_text
    )
    page.resources.click_join_addon_review_link()
    page.wait_for_current_url("/Add-ons/Contribute/Code")


# @pytest.mark.nondestructive
# @pytest.mark.create_session("developer")
# def test_devhub_resources_write_some_code(selenium, base_url, variables):
#     page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
#     assert "More Ways to Participate" in page.resources.write_code_section_header
#     assert (
#         variables["devhub_resources_write_some_code_text"]
#         in page.resources.write_code_section_info_text
#     )
#     page.resources.click_write_code_section_link()
#     page.wait_for_current_url("/Add-ons/Contribute/Code")


@pytest.mark.nondestructive
def test_devhub_resources_participate(selenium, base_url, variables):
    """Ensures that the "More Ways to Participate" link
    in the resources section redirects the user to the
    "Add-ons/Contribute" section."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login("regular_user")
    assert "More Ways to Participate" in page.resources.participate_section_header
    assert (
        variables["devhub_resources_participate_text"]
        in page.resources.participate_section_info_text
    )
    page.resources.click_participate_section_link()
    page.wait_for_current_url("/Add-ons/Contribute")



# @pytest.mark.parametrize(
#     "count, link",
#     enumerate(
#         [
#             # twitter requires login atm so no direct landing
#             # on the mozilla tweeters is available right now
#             # we are checking that a redirect to twitter happens
#             "x.com",
#             "x.com",
#         ]
#     ),
# )
# @pytest.mark.nondestructive
# def test_page_connect_footer_twitter(selenium, base_url, count, link):
#     page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
#     assert "Connect with us" in page.connect.connect_footer_title
#     assert "Twitter" in page.connect.connect_twitter_title
#     page.connect.twitter_links[count].click()
#     assert link in selenium.current_url


@pytest.mark.parametrize(
    "count, link",
    enumerate(
        [
            "chat.mozilla.org/#/room/#addons:mozilla.org",
            "discourse.mozilla.org/c/add-ons/",
        ]
    ),
    ids=[
        "AMO Matrix channel",
        "Mozilla Discourse",
    ],
)
@pytest.mark.nondestructive
def test_page_connect_footer_more_links(selenium, base_url, count, link):
    """Ensures that all "More" links in the footer under
    the "Connect" section lead to the correct pages,
    such as the Mozilla Matrix channel or Discourse forums."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # assert "More" in page.connect.connect_more_title
    page.connect.more_connect_links[count].click()
    assert link in selenium.current_url


@pytest.mark.nondestructive
def test_connect_newsletter_section(selenium, base_url, variables):
    """Verifies the content and functionality of the newsletter signup
    section in the footer, ensuring that the privacy notice link works
    and that the user is able to sign up for the newsletter."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # verifies the elements of the Newsletter signup section
    assert (
        variables["devhub_newsletter_header"] in page.connect.newsletter_section_header
    )
    assert variables["devhub_newsletter_info_text"] in page.connect.newsletter_info_text
    # verify that the Privacy notice links opens the right page
    page.connect.click_newsletter_privacy_notice_link()
    page.wait_for_current_url("/privacy/websites/")


@pytest.mark.nondestructive
@pytest.mark.skip(
    reason= "Skipped until this issue is fixed: https://github.com/mozilla/addons-server/issues/21335"
)
def test_verify_newsletter_signup_confirmation(selenium, base_url, variables, wait):
    """Ensures that after signing up for the newsletter,
    the user receives a confirmation message,
    and that a confirmation email is sent
    to the provided email address."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    email = f"{reusables.get_random_string(10)}@restmail.net"
    # fill in the newsletter subscription form
    page.connect.newsletter_email_input_field(email)
    page.connect.click_privacy_checkbox()
    page.connect.newsletter_sign_up.click()
    # checks that the form transitions to confirmation messages after clicking Sign up
    wait.until(EC.invisibility_of_element(page.connect.newsletter_sign_up))
    assert (
        variables["devhub_signup_confirmation_title"]
        in page.connect.newsletter_signup_confirmation_header
    )
    assert (
        variables["devhub_signup_confirmation_message"]
        in page.connect.newsletter_signup_confirmation_message
    )
    # verify that a confirmation email was received after subscribing
    confirmation_email = page.connect.check_newsletter_signup_email(email)
    assert "Action Required: Confirm Your Subscription" in confirmation_email


@pytest.mark.nondestructive
def test_devhub_mozilla_footer_link(base_url, selenium):
    """Verifies that clicking on the "Mozilla" link in
    the DevHub footer redirects the user to the Mozilla homepage."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.footer.mozilla_link.click()
    assert "mozilla.org" in selenium.current_url


@pytest.mark.parametrize(
    "count, link",
    enumerate(
        [
            "about",
            "/blog",
            "extensionworkshop",
            "developers",
            "add-on-policies",
            "addons",
            "discourse",
            "/about",
            "review_guide",
        ]
    ),
    ids=[
        "DevHub Footer - Addons section -  About",
        "DevHub Footer - Addons section -  Blog",
        "DevHub Footer - Addons section -  Extension Workshop",
        "DevHub Footer - Addons section -  Developer Hub",
        "DevHub Footer - Addons section -  Developer Policies",
        "DevHub Footer - Addons section -  Community Blog",
        "DevHub Footer - Addons section -  Forum",
        "DevHub Footer - Addons section -  Report a bug",
        "DevHub Footer - Addons section -  Review Guide",
    ],
)
@pytest.mark.nondestructive
def test_devhub_addons_footer_links(base_url, selenium, count, link):
    """Ensures that the links under the "Add-ons" section
    in the DevHub footer lead to the correct pages,
    such as About, Blog, Extension Workshop, etc."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.footer.addon_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    "count, link",
    enumerate(
        [
            "en-US/?redirect_source=mozilla-org&utm_campaign=SET_DEFAULT_BROWSER",
            "en-US/browsers/mobile/",
            "en-US/browsers/enterprise/",
        ]
    ),
    ids=[
        "DevHub Footer - Browsers section -  Desktop",
        "DevHub Footer - Browsers section -  Mobile",
        "DevHub Footer - Browsers section -  Enterprise",
    ],
)
@pytest.mark.nondestructive
def test_devhub_browsers_footer_links(base_url, selenium, count, link):
    """Verifies that the links under the "Browsers" section
    in the DevHub footer lead to the correct pages
    for Firefox Desktop, Mobile, and Enterprise."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.footer.browsers_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    "count, link",
    enumerate(
        [
            "en-US/?utm_campaign=SET_DEFAULT_BROWSER",
            "products/vpn/",
            "relay.firefox.com/",
            "monitor.mozilla",
            "getpocket.com",
        ]
    ),
    ids=[
        "DevHub Footer - Products section -  Browsers",
        "DevHub Footer - Products section -  VPN",
        "DevHub Footer - Products section -  Relay",
        "DevHub Footer - Products section -  Monitor",
        "DevHub Footer - Products section -  Pocket",
    ],
)
@pytest.mark.nondestructive
def test_devhub_products_footer_links(base_url, selenium, count, link):
    """Ensures that the links under the "Products" section
    in the DevHub footer lead to the correct pages for
    Firefox, VPN, Relay, Monitor, and Pocket."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.products_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    "count, link",
    enumerate(
        [
            "x.com",
            "instagram.com",
            "youtube.com",
        ]
    ),
    ids=[
        "DevHub Footer - Social section -  Twitter",
        "DevHub Footer - Social section -  Instagram",
        "DevHub Footer - Social section -  YouTube",
    ],
)
@pytest.mark.nondestructive
def test_devhub_social_footer_links(base_url, selenium, count, link):
    """Verifies that the social media links in the DevHub footer
    direct users to the correct social media pages."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.footer.social_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    "count, link",
    enumerate(
        [
            "privacy/websites/",
            "privacy/websites/",
            "legal/amo-policies/",
        ]
    ),
    ids=[
        "DevHub Footer - Legal section -  Privacy",
        "DevHub Footer - Legal section -  Cookies",
        "DevHub Footer - Legal section -  Legal",
    ],
)
@pytest.mark.nondestructive
def test_devhub_legal_footer_links(base_url, selenium, count, link):
    """Ensures that the legal links in the DevHub footer
    direct users to the correct legal and policy pages."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.footer.legal_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    "language, locale, translation",
    [
        ("Français", "fr", "Pôle développeurs de modules"),
        ("Deutsch", "de", "Add-on-Entwicklerzentrum"),
        ("中文 (简体)", "zh-CN", "附加组件开发者中心"),
        ("Русский", "ru", "Разработчикам дополнений"),
        ("עברית", "he", "מרכז מפתחי תוספות"),
    ],
    ids=[
        "DevHub French Translation",
        "DevHub German Translation",
        "DevHub Chinese Translation",
        "DevHub Russian Translation",
        "DevHub Hebrew Translation",
    ],
)
@pytest.mark.nondestructive
def test_change_devhub_language(base_url, selenium, language, locale, translation):
    """Verifies that changing the language in the DevHub footer
    correctly updates the locale and displays the translated page,
    confirming the correct language and content."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.footer_language_picker(language)
    assert f"{locale}/developers/" in selenium.current_url
    assert translation in page.page_logo.text


@pytest.mark.parametrize(
    "count, link",
    enumerate(
        [
            ["/about/legal/", ".mzp-c-article-title"],
            ["/licenses/by-sa/3.0/", ".identity-logo"],
        ]
    ),
    ids=[
        "Legal",
        "Creative Commons License",
    ],
)
@pytest.mark.nondestructive
def test_devhub_footer_copyright_message(base_url, selenium, count, link, wait):
    """Ensures that the copyright message in the DevHub footer
    is displayed correctly and that the linked pages
     open as expected."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    assert page.footer.copyright_message.is_displayed()
    page.footer.copyright_links[count].click()
    page.wait_for_current_url(link[0])
    page.wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, link[1])),
        message=f'The chosen element "{link[1]}" could not be loaded on the "{link[0]}" webpage',
    )


@pytest.mark.sanity
@pytest.mark.nondestructive
@pytest.mark.create_session("developer")
def test_devhub_logout_tc_id_c15075(selenium, base_url, wait):
    """Verifies that clicking the "Sign Out" button logs the user
    out of DevHub and that the login button is displayed afterward,
    confirming successful logout."""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # page.devhub_login("developer")
    page.click_sign_out()
    # confirms user is no longer logged in
    wait.until(lambda _: page.header_login_button.is_displayed())
