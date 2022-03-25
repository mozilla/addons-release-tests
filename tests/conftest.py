import os

import pytest

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.frontend.home import Home
from pages.desktop.frontend.login import Login

# Window resolutions
DESKTOP = (1920, 1080)


@pytest.fixture(scope='session')
def base_url(base_url, variables):
    return variables['base_url']


@pytest.fixture(scope='session')
def sensitive_url(request, base_url):
    # Override sensitive url check
    return False


@pytest.fixture
def firefox_options(firefox_options, request):
    """Firefox options.

    These options configure firefox to allow for addon installation,
    as well as allowing it to run headless.

    'extensions.install.requireBuiltInCerts', False: This allows extensions to
        be installed with a self-signed certificate.
    'xpinstall.signatures.required', False: This allows an extension to be
        installed without a certificate.
    'extensions.webapi.testing', True: This is needed for whitelisting
        mozAddonManager
    '-foreground': Firefox will run in the foreground with priority
    '-headless': Firefox will run headless

    """
    # for prod installation tests, we do not need to set special prefs,
    # so I've added a custom marker which will allow the Firefox
    # driver to run a clean profile for prod tests, when necessary
    marker = request.node.get_closest_marker('firefox_release')
    if marker:
        firefox_options.add_argument('-headless')
        firefox_options.log.level = 'trace'
        firefox_options.set_preference(
            'extensions.getAddons.discovery.api_url',
            'https://services.addons.mozilla.org/api/v4/discovery/?lang=%LOCALE%&edition=%DISTRIBUTION%',
        )
        firefox_options.set_preference('extensions.getAddons.cache.enabled', True)
    else:
        firefox_options.set_preference('extensions.install.requireBuiltInCerts', False)
        firefox_options.set_preference('xpinstall.signatures.required', False)
        firefox_options.set_preference('xpinstall.signatures.dev-root', True)
        firefox_options.set_preference('extensions.webapi.testing', True)
        firefox_options.set_preference('ui.popup.disable_autohide', True)
        firefox_options.set_preference('devtools.console.stdout.content', True)
        firefox_options.add_argument('-headless')
        firefox_options.log.level = 'trace'
    return firefox_options


@pytest.fixture
def firefox_notifications(notifications):
    return notifications


@pytest.fixture(
    scope='function',
    params=[DESKTOP],
    ids=['Desktop'],
)
def selenium(selenium, base_url, session_auth, request):
    """Fixture to set a custom resolution for tests running on Desktop
    and handle browser sessions when needed"""
    selenium.set_window_size(*request.param)
    # establishing actions  based on markers
    create_session = request.node.get_closest_marker('create_session')
    login = request.node.get_closest_marker('login')
    clear_session = request.node.get_closest_marker('clear_session')
    # this is used when we want to open an AMO page with a sessionid
    # cookie (i.e. a logged-in user) already set
    if create_session:
        # need to set the url context if we want to apply a cookie
        # in order to avoid InvalidCookieDomainException error
        selenium.get(base_url)
        # set the sessionid cookie
        selenium.add_cookie(
            {
                "name": "sessionid",
                "value": session_auth,
            }
        )
    # this is used when we want to start the browser with a normal login
    # mostly used for the scope of getting the session cookie and storing it for later use
    if login:
        home = Home(selenium, base_url).open().wait_for_page_to_load()
        home.header.click_login()
        home.wait.until(
            EC.visibility_of_element_located((By.NAME, 'email')),
            message=f'FxA email input field was not displayed in {selenium.current_url}',
        )
        user = login.args[0]
        Login(selenium, base_url).account(user)
        home.wait.until(
            EC.url_contains('addons'),
            message=f'AMO could not be loaded in {selenium.current_url}',
        )
        session_cookie = selenium.get_cookie('sessionid')
        with open(user + '.txt', 'w') as file:
            file.write(session_cookie['value'])
    # delete the user session and files created for a test suite;
    # this is normally used as the last step in a test suite
    if clear_session:
        # clear session
        home = Home(selenium, base_url).open().wait_for_page_to_load()
        home.header.click_logout()
        # delete the file
        user_file = create_session.args[0]
        import os

        if os.path.exists(f'{user_file}.txt'):
            os.remove(f'{user_file}.txt')
        else:
            print("The file does not exist")
    return selenium


@pytest.fixture(scope='function')
def session_auth(request):
    """Fixture that reads and returns the sessionid cookie; to be used as a
    standalone fixture for in API tests that require authentication and
    also complements the selenium fixture  when we want to start
    the browser with an active user session"""
    marker = request.node.get_closest_marker('create_session')
    # the user file is passed in the test as a marker argument
    if marker:
        user_file = marker.args[0]
        with open(f'{user_file}.txt', 'r') as file:
            sessionid = str(file.read())
        return sessionid


@pytest.fixture
def wait():
    """A preset wait to be used in test methods. Removes the necessity to declare a
    WebDriverWait whenever we need to wait for certain conditions to happen in a test"""
    return WebDriverWait(
        selenium, 10, ignored_exceptions=StaleElementReferenceException
    )


@pytest.fixture
def fxa_account(request):
    """Fxa account to use during tests that need to login.

    Returns the email and password of the fxa account set in Makefile-docker.

    """
    try:
        fxa_account.email = os.environ['UITEST_FXA_EMAIL']
        fxa_account.password = os.environ['UITEST_FXA_PASSWORD']
    except KeyError:
        if request.node.get_closest_marker('fxa_login'):
            pytest.skip(
                'Skipping test because no fxa account was found.'
                ' Are FXA_EMAIL and FXA_PASSWORD environment variables set?'
            )
    return fxa_account
