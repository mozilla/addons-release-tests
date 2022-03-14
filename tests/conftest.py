import os

import pytest


# Window resolutions
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait

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
def selenium(selenium, request):
    """Fixture to set a custom resolution for tests running on Desktop."""
    selenium.set_window_size(*request.param)
    return selenium


@pytest.fixture
def wait():
    """A preset wait to be used in test methods. Removes the necessity to declare a
    WebDriverWait whenever we need to wait for certain conditions to happen in a test"""
    return WebDriverWait(
        selenium, 10, ignored_exceptions=StaleElementReferenceException
    )


@pytest.fixture
def set_session_cookie(selenium, base_url, request):
    """Fixture used when we want to open an AMO page with a sessionid
    cookie (i.e. a logged-in user) already set"""
    # the user file is passed in the test as a marker argument
    marker = request.node.get_closest_marker('user_data')
    user_file = marker.args[0]
    with open(f'{user_file}.txt', 'r') as file:
        cookie_value = str(file.read())
    # need to set the url context if we want to apply a cookie
    # in order to avoid InvalidCookieDomainException error
    selenium.get(base_url)
    # set the sessionid cookie
    create_session = selenium.add_cookie(
        {
            "name": "sessionid",
            "value": cookie_value,
        }
    )
    return create_session


@pytest.fixture
def destroy_file(request):
    """Fixture to delete user files created for a test suite"""
    marker = request.node.get_closest_marker('user_data')
    user_file = marker.args[0]
    import os

    if os.path.exists(f'{user_file}.txt'):
        os.remove(f'{user_file}.txt')
    else:
        print("The file does not exist")


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
