import pytest

from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.devhub import DevHub
from scripts import reusables


@pytest.mark.nondestructive
def test_devhub_logo(selenium, base_url):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    # clicks on the page logo and verifies page is reloaded
    page.page_logo.click()
    assert page.page_logo.is_displayed()


@pytest.mark.nondestructive
def test_click_extension_workshop(selenium, base_url):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    # clicks on EW in the header menu and checks page is loaded
    page.extension_workshop.click()
    page.extension_workshop_is_loaded()


@pytest.mark.nondestructive
def test_click_documentation(selenium, base_url):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    # clicks on Documentation header menu and checks page is loaded
    page.click_documentation()


@pytest.mark.nondestructive
def test_click_support(selenium, base_url):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    # clicks on Support header menu and checks page is loaded
    page.click_support()
    page.wait_for_current_url('Add-ons#Get_in_touch')


@pytest.mark.nondestructive
def test_click_blog(selenium, base_url):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    # clicks on Blog header menu and checks page is loaded
    page.click_blog()


@pytest.mark.nondestructive
def test_devhub_login(selenium, base_url, wait):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login('developer')
    # verifies that the user has been logged in by looking at the user icon
    wait.until(lambda _: page.user_avatar.is_displayed())


@pytest.mark.nondestructive
def test_devhub_logout(selenium, base_url, wait):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login('developer')
    page.click_sign_out()
    # confirms user is no longer logged in
    wait.until(lambda _: page.header_login_button.is_displayed())


@pytest.mark.nondestructive
def test_devhub_page_overview(selenium, base_url, variables):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    # checks the content in the page 'Overview' - main section
    assert variables['devhub_overview_header'] in page.devhub_overview_title
    assert variables['devhub_overview_summary'] in page.devhub_overview_summary
    page.click_overview_learn_how_button()
    # checks that the link redirects to the extension workshop
    page.extension_workshop_is_loaded()


@pytest.mark.nondestructive
def test_devhub_page_content(selenium, base_url, variables):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    # checks the content in the page 'Content' - secondary section
    assert variables['devhub_content_header'] in page.devhub_content_title
    assert variables['devhub_content_summary'] in page.devhub_content_summary
    assert page.devhub_content_image.is_displayed()


@pytest.mark.nondestructive
def test_devhub_content_login_link(selenium, base_url, variables):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    page.click_content_login_link()
    # verify that the link opens the FxA login page
    page.wait_for_current_url('accounts.firefox.com')


@pytest.mark.nondestructive
def test_devhub_page_get_involved(selenium, base_url, variables):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    # checks the content in the page 'Get Involved' - secondary section
    assert variables['devhub_get_involved_header'] in page.devhub_get_involved_title
    assert variables['devhub_get_involved_summary'] in page.devhub_get_involved_summary
    assert page.devhub_get_involved_image.is_displayed()
    page.devhub_get_involved_link.click()
    page.wait_for_title_update('Add-ons/Contribute')


@pytest.mark.parametrize(
    'count, link',
    enumerate(
        [
            'twitter.com/mozamo',
            'twitter.com/rockyourfirefox',
        ]
    ),
)
@pytest.mark.nondestructive
def test_page_connect_footer_twitter(selenium, base_url, count, link):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    assert 'Connect with us' in page.connect.connect_footer_title
    assert 'Twitter' in page.connect.connect_twitter_title
    page.connect.twitter_links[count].click()
    assert link in selenium.current_url


@pytest.mark.parametrize(
    'count, link',
    enumerate(
        [
            'chat.mozilla.org/#/room/#addons:mozilla.org',
            'discourse.mozilla.org/c/add-ons/',
        ]
    ),
    ids=[
        'AMO Matrix channel',
        'Mozilla Discourse',
    ],
)
@pytest.mark.nondestructive
def test_page_connect_footer_more_links(selenium, base_url, count, link):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    assert 'More' in page.connect.connect_more_title
    page.connect.more_connect_links[count].click()
    assert link in selenium.current_url


@pytest.mark.nondestructive
def test_connect_newsletter_section(selenium, base_url, variables):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    # verifies the elements of the Newsletter signup section
    assert (
        variables['devhub_newsletter_header'] in page.connect.newsletter_section_header
    )
    assert variables['devhub_newsletter_info_text'] in page.connect.newsletter_info_text
    # verify that the Privacy notice links opens the right page
    page.connect.click_newsletter_privacy_notice_link()
    page.wait_for_current_url('/privacy/websites/')


@pytest.mark.nondestructive
def test_verify_newsletter_signup_confirmation(selenium, base_url, variables, wait):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    email = f'{reusables.get_random_string(10)}@restmail.net'
    # fill in the newsletter subscription form
    page.connect.newsletter_email_input_field(email)
    page.connect.click_privacy_checkbox()
    page.connect.newsletter_sign_up.click()
    # checks that the form transitions to confirmation messages after clicking Sign up
    wait.until(EC.invisibility_of_element(page.connect.newsletter_sign_up))
    assert (
        variables['devhub_signup_confirmation_title']
        in page.connect.newsletter_signup_confirmation_header
    )
    assert (
        variables['devhub_signup_confirmation_message']
        in page.connect.newsletter_signup_confirmation_message
    )
    # verify that a confirmation email was received after subscribing
    confirmation_email = page.connect.check_newsletter_signup_email(email)
    assert 'Action Required: Confirm Your Subscription' in confirmation_email


@pytest.mark.nondestructive
def test_devhub_mozilla_footer_link(base_url, selenium):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    page.footer.mozilla_link.click()
    assert 'mozilla.org' in selenium.current_url


@pytest.mark.parametrize(
    'count, link',
    enumerate(
        [
            'about',
            'blog.mozilla.org',
            'extensionworkshop',
            'developers',
            'add-on-policies',
            'discourse',
            '/about',
            'review_guide',
            'mozilla.org',  # temporary
        ]
    ),
    ids=[
        'DevHub Footer - Addons section -  About',
        'DevHub Footer - Addons section -  Blog',
        'DevHub Footer - Addons section -  Extension Workshop',
        'DevHub Footer - Addons section -  Developer Hub',
        'DevHub Footer - Addons section -  Developer Policies',
        'DevHub Footer - Addons section -  Forum',
        'DevHub Footer - Addons section -  Report a bug',
        'DevHub Footer - Addons section -  Review Guide',
        'DevHub Footer - Addons section -  Site status',
    ],
)
@pytest.mark.nondestructive
def test_devhub_addons_footer_links(base_url, selenium, count, link):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    page.footer.addon_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    'count, link',
    enumerate(
        [
            'firefox/new',
            'firefox/browsers/mobile/',
            'mixedreality.mozilla.org',
            'firefox/enterprise/',
        ]
    ),
    ids=[
        'DevHub Footer - Browsers section -  Desktop',
        'DevHub Footer - Browsers section -  Mobile',
        'DevHub Footer - Browsers section -  Reality',
        'DevHub Footer - Browsers section -  Enterprise',
    ],
)
@pytest.mark.nondestructive
def test_devhub_browsers_footer_links(base_url, selenium, count, link):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    page.footer.browsers_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    'count, link',
    enumerate(
        [
            'firefox/browsers/',
            'products/vpn/',
            'relay.firefox.com/',
            'monitor.firefox',
            'getpocket.com',
        ]
    ),
    ids=[
        'DevHub Footer - Products section -  Browsers',
        'DevHub Footer - Products section -  VPN',
        'DevHub Footer - Products section -  Relay',
        'DevHub Footer - Products section -  Monitor',
        'DevHub Footer - Products section -  Pocket',
    ],
)
@pytest.mark.nondestructive
def test_devhub_products_footer_links(base_url, selenium, count, link):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    page.products_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    'count, link',
    enumerate(
        [
            'twitter.com',
            'instagram.com',
            'youtube.com',
        ]
    ),
    ids=[
        'DevHub Footer - Social section -  Twitter',
        'DevHub Footer - Social section -  Instagram',
        'DevHub Footer - Social section -  YouTube',
    ],
)
@pytest.mark.nondestructive
def test_devhub_social_footer_links(base_url, selenium, count, link):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    page.footer.social_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    'count, link',
    enumerate(
        [
            'privacy/websites/',
            'privacy/websites/',
            'legal/terms/mozilla',
        ]
    ),
    ids=[
        'DevHub Footer - Legal section -  Privacy',
        'DevHub Footer - Legal section -  Cookies',
        'DevHub Footer - Legal section -  Legal',
    ],
)
@pytest.mark.nondestructive
def test_devhub_legal_footer_links(base_url, selenium, count, link):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    page.footer.legal_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    'language, locale, translation',
    [
        ('Français', 'fr', 'Pôle développeurs de modules'),
        ('Deutsch', 'de', 'Add-on-Entwicklerzentrum'),
        ('中文 (简体)', 'zh-CN', '附加组件开发者中心'),
        ('Русский', 'ru', 'Разработчикам дополнений'),
        ('עברית', 'he', 'מרכז מפתחי תוספות'),
    ],
    ids=[
        'DevHub French Translation',
        'DevHub German Translation',
        'DevHub Chinese Translation',
        'DevHub Russian Translation',
        'DevHub Hebrew Translation',
    ],
)
@pytest.mark.nondestructive
def test_change_devhub_language(base_url, selenium, language, locale, translation):
    page = DevHub(selenium, base_url).open().wait_for_page_to_load()
    page.footer_language_picker(language)
    assert f'{locale}/developers/' in selenium.current_url
    assert translation in page.page_logo.text
