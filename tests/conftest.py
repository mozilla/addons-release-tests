import os

import pytest
import requests

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.frontend.home import Home
from pages.desktop.frontend.login import Login

# Window resolutions
DESKTOP = (1920, 1080)


@pytest.fixture(scope="session")
def base_url(base_url, variables):
    return variables["base_url"]


@pytest.fixture(scope="session")
def sensitive_url(request, base_url):
    # Override sensitive url check
    return False


@pytest.fixture
def firefox_options(firefox_options, base_url, variables):
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
    # for prod installation tests, we do not need to set special prefs, so we
    # separate the browser set-up based on the AMO environments
    if base_url == "https://addons.mozilla.org":
        firefox_options.add_argument("-foreground")
        firefox_options.log.level = "trace"
        firefox_options.set_preference(
            "extensions.getAddons.discovery.api_url",
            "https://services.addons.mozilla.org/api/v4/discovery/?lang=%LOCALE%&edition=%DISTRIBUTION%",
        )
        firefox_options.set_preference("extensions.getAddons.cache.enabled", True)
        firefox_options.set_preference(
            "extensions.getAddons.get.url",
            "https://services.addons.mozilla.org/api/v4/addons/search/?guid=%IDS%&lang=%LOCALE%",
        )
        firefox_options.set_preference(
            "extensions.update.url",
            "extensions.update.url	https://versioncheck.addons.mozilla.org/update/VersionCheck.php?reqVersion=%REQ_VERSION%&id=%ITEM_ID%&version=%ITEM_VERSION%&maxAppVersion=%ITEM_MAXAPPVERSION%&status=%ITEM_STATUS%&appID=%APP_ID%&appVersion=%APP_VERSION%&appOS=%APP_OS%&appABI=%APP_ABI%&locale=%APP_LOCALE%&currentAppVersion=%CURRENT_APP_VERSION%&updateType=%UPDATE_TYPE%&compatMode=%COMPATIBILITY_MODE%"
        )
        firefox_options.set_preference(
            "extensions.update.background.url",
            "https://versioncheck-bg.addons.mozilla.org/update/VersionCheck.php?reqVersion=%REQ_VERSION%&id=%ITEM_ID%&version=%ITEM_VERSION%&maxAppVersion=%ITEM_MAXAPPVERSION%&status=%ITEM_STATUS%&appID=%APP_ID%&appVersion=%APP_VERSION%&appOS=%APP_OS%&appABI=%APP_ABI%&locale=%APP_LOCALE%&currentAppVersion=%CURRENT_APP_VERSION%&updateType=%UPDATE_TYPE%&compatMode=%COMPATIBILITY_MODE%"
        )
    else:
        firefox_options.set_preference("extensions.install.requireBuiltInCerts", False)
        firefox_options.set_preference("xpinstall.signatures.required", True)
        firefox_options.set_preference("xpinstall.signatures.dev-root", True)
        firefox_options.set_preference("extensions.webapi.testing", True)
        firefox_options.set_preference("ui.popup.disable_autohide", True)
        firefox_options.set_preference("devtools.console.stdout.content", True)
        firefox_options.set_preference(
            "extensions.getAddons.discovery.api_url",
            variables["extensions_getAddons_discovery_api_url"],
        )
        firefox_options.set_preference(
            "extensions.getAddons.get.url",
            variables["extensions_getAddons_get_url"],
        )
        firefox_options.set_preference(
            "extensions.update.url", variables["extensions_update_url"]
        )
        firefox_options.add_argument("-foreground")
        firefox_options.log.level = "trace"
    return firefox_options


@pytest.fixture
def firefox_notifications(notifications):
    return notifications


@pytest.fixture(
    scope="function",
    params=[DESKTOP],
    ids=["Desktop"],
)
def selenium(selenium, base_url, session_auth, request):
    """Fixture to set a custom resolution for tests running on Desktop
    and handle browser sessions when needed"""
    selenium.set_window_size(*request.param)
    # establishing actions  based on markers
    create_session = request.node.get_closest_marker("create_session")
    login = request.node.get_closest_marker("login")
    clear_session = request.node.get_closest_marker("clear_session")
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
            EC.visibility_of_element_located((By.NAME, "email")),
            message=f"FxA email input field was not displayed in {selenium.current_url}",
        )
        user = login.args[0]
        Login(selenium, base_url).account(user)
        home.wait.until(
            EC.url_contains("addons"),
            message=f"AMO could not be loaded in {selenium.current_url}",
        )
        session_cookie = selenium.get_cookie("sessionid")
        with open(user + ".txt", "w") as file:
            file.write(session_cookie["value"])
    yield selenium

    # delete the user session and files created for a test suite;
    # this is normally used in the last test of a suite to handle the clean-up part
    if clear_session:
        # clear session by calling the DELETE session API
        delete_session = requests.delete(
            url=f"{base_url}/api/v5/accounts/session/",
            headers={"Authorization": f"Session {session_auth}"},
        )
        assert (
            delete_session.status_code == 200
        ), f"Actual status code was {delete_session.status_code}"
        # test that session was invalidated correctly by trying to access the account with the deleted session
        get_user = requests.get(
            url=f"{base_url}/api/v5/accounts/profile/",
            headers={"Authorization": f"Session {session_auth}"},
        )
        assert (
            get_user.status_code == 401
        ), f"Actual status code was {get_user.status_code}"
        assert (
            "Valid user session not found matching the provided session key."
            in get_user.text
        ), f"Actual response message was {get_user.text}"
        user_file = create_session.args[0]
        if os.path.exists(f"{user_file}.txt"):
            os.remove(f"{user_file}.txt")
        else:
            # fail if the file does not exist
            raise FileNotFoundError("The file does not exist")


@pytest.fixture(scope="function")
def session_auth(request):
    """Fixture that reads and returns the sessionid cookie; to be used as a
    standalone fixture for in API tests that require authentication and
    also complements the selenium fixture  when we want to start
    the browser with an active user session"""
    marker = request.node.get_closest_marker("create_session")
    # the user file is passed in the test as a marker argument
    if marker:
        user_file = marker.args[0]
        with open(f"{user_file}.txt", "r") as file:
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
def delete_themes(selenium, base_url):
    """Use this fixture in devhub theme submission tests when we want to
    immediately delete the theme once the test has completed"""
    yield

    from pages.desktop.developers.devhub_home import DevHubHome

    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    manage_addons = page.click_my_addons_header_link()
    manage_addons.click_on_my_themes()
    while len(manage_addons.addon_list) > 0:
        addon = manage_addons.addon_list[0]
        edit = addon.click_addon_name()
        manage = edit.click_manage_versions_link()
        delete = manage.delete_addon()
        delete.input_delete_confirmation_string()
        delete.confirm_delete_addon()
