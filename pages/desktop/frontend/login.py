import os
import time
import requests
import pyotp

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base
from scripts import reusables


class Login(Base):
    """The following variables need to be set as Environment Variables
     when running tests locally. These variables are also set in CircleCI's
    Project level Environment Variables and are picked up at runtime"""

    # 1. user that performs normal operations on the site, like writing add-on reviews
    REGULAR_USER_EMAIL = os.environ.get("REGULAR_USER_EMAIL")
    REGULAR_USER_PASSWORD = os.environ.get("REGULAR_USER_PASSWORD")
    # 2. user with elevated permissions that can perform special actions on the site
    ADMIN_USER_EMAIL = os.environ.get("ADMIN_USER_EMAIL")
    ADMIN_USER_PASSWORD = os.environ.get("ADMIN_USER_PASSWORD")
    # 3. user who has published add-ons on AMO
    DEVELOPER_EMAIL = os.environ.get("DEVELOPER_EMAIL")
    DEVELOPER_PASSWORD = os.environ.get("DEVELOPER_PASSWORD")
    # 4. user who re-creates accounts on AMO after having deleted them previously
    REUSABLE_USER_EMAIL = os.environ.get("REUSABLE_USER_EMAIL")
    REUSABLE_USER_PASSWORD = os.environ.get("REUSABLE_USER_PASSWORD")
    # 5. user used for the ratings tests
    RATING_USER_EMAIL = os.environ.get("RATING_USER_EMAIL")
    RATING_USER_PASSWORD = os.environ.get("RATING_USER_PASSWORD")
    # 6. user used for collections tests
    COLLECTION_USER_EMAIL = os.environ.get("COLLECTION_USER_EMAIL")
    COLLECTION_USER_PASSWORD = os.environ.get("COLLECTION_USER_PASSWORD")
    # 7. user used for add-on submissions
    SUBMISSIONS_USER_EMAIL = os.environ.get("SUBMISSIONS_USER_EMAIL")
    SUBMISSIONS_USER_PASSWORD = os.environ.get("SUBMISSIONS_USER_PASSWORD")
    # 8. user used in API tests
    API_USER_EMAIL = os.environ.get("API_USER_EMAIL")
    API_USER_PASSWORD = os.environ.get("API_USER_PASSWORD")
    # 9. user with a mozilla account that has specific submission permissions
    STAFF_USER_EMAIL = os.environ.get("STAFF_USER_EMAIL")
    STAFF_USER_PASSWORD = os.environ.get("STAFF_USER_PASSWORD")
    # 10. account added to the list of banned user emails for rating and addon submissions
    RESTRICTED_USER_EMAIL = os.environ.get("RESTRICTED_USER_EMAIL")
    RESTRICTED_USER_PASSWORD = os.environ.get("RESTRICTED_USER_PASSWORD")
    # 11. account for reviewer tools added in order to help with release and coverage tests(doesn't have full access)
    REVIEWER_TOOLS_USER_EMAIL = os.environ.get("REVIEWER_TOOLS_USER_EMAIL")
    REVIEWER_TOOLS_USER_PASSWORD = os.environ.get("REVIEWER_TOOLS_USER_PASSWORD")

    # KEYS FOR AUTHENTICATOR DEV
    DEVELOPER_USER_KEY_DEV = os.environ.get("DEVELOPER_USER_KEY_DEV")
    RATING_USER_KEY_DEV = os.environ.get("RATING_USER_KEY_DEV")
    SUBMISSIONS_USER_KEY_DEV = os.environ.get("SUBMISSIONS_USER_KEY_DEV")
    API_USER_KEY_DEV = os.environ.get("API_USER_KEY_DEV")
    STAFF_USER_KEY_DEV = os.environ.get("STAFF_USER_KEY_DEV")
    # KEYS FOR AUTHENTICATOR STAGE
    DEVELOPER_USER_KEY_STAGE = os.environ.get("DEVELOPER_USER_KEY_STAGE")
    RATING_USER_KEY_STAGE = os.environ.get("RATING_USER_KEY_STAGE")
    SUBMISSIONS_USER_KEY_STAGE = os.environ.get("SUBMISSIONS_USER_KEY_STAGE")
    API_USER_KEY_STAGE = os.environ.get("API_USER_KEY_STAGE")
    STAFF_USER_KEY_STAGE = os.environ.get("STAFF_USER_KEY_STAGE")
    REVIEWER_TOOLS_USER_KEY = os.environ.get("REVIEWER_TOOLS_USER_KEY")

    _email_locator = (By.NAME, "email")
    _continue_locator = (By.CSS_SELECTOR, ".button-row button")
    _password_login = (By.CSS_SELECTOR, ".pb-1")
    _password_locator = (By.XPATH, "//input[@data-testid='new-password-input-field']")
    _login_btn_locator = (By.CSS_SELECTOR, "button.cta-primary.cta-xl")
    _repeat_password_locator = (By.CSS_SELECTOR, "div.relative:nth-child(3) > div:nth-child(1) > label:nth-child(1) > span:nth-child(1) > input:nth-child(2)")
    _age_locator = (By.XPATH, "//input[@data-testid='age-input-field']")
    _code_input_locator = (By.CSS_SELECTOR, ".pb-1")
    _login_card_header_locator = (By.CSS_SELECTOR, ".card-header")
    _2fa_input_locator = (By.CSS_SELECTOR, ".pb-1")
    _confirm_2fa_button_locator = (By.CSS_SELECTOR, ".cta-primary")
    _error_2fa_code_locator = (By.CSS_SELECTOR, ".text-xs")

    @property
    def click_login_button(self):
        self.wait_for_element_to_be_displayed(self._login_btn_locator)
        return self.find_element(*self._login_btn_locator).click()

    def account(self, user):
        if user == "reusable_user":
            self.fxa_login(self.REUSABLE_USER_EMAIL, self.REUSABLE_USER_PASSWORD, "")
        elif user == "admin":
            self.fxa_login(self.ADMIN_USER_EMAIL, self.ADMIN_USER_PASSWORD, "")
        elif user == "developer":
            if "dev.allizom" not in self.base_url:
                self.fxa_login(
                    self.DEVELOPER_EMAIL,
                    self.DEVELOPER_PASSWORD,
                    self.DEVELOPER_USER_KEY_STAGE,
                )
            else:
                self.fxa_login(
                    self.DEVELOPER_EMAIL,
                    self.DEVELOPER_PASSWORD,
                    self.DEVELOPER_USER_KEY_DEV,
                )
        elif user == "rating_user":
            if "dev.allizom" not in self.base_url:
                self.fxa_login(
                    self.RATING_USER_EMAIL,
                    self.RATING_USER_PASSWORD,
                    self.RATING_USER_KEY_STAGE,
                )
            else:
                self.fxa_login(
                    self.RATING_USER_EMAIL,
                    self.RATING_USER_PASSWORD,
                    self.RATING_USER_KEY_DEV,
                )
        elif user == "collection_user":
            self.fxa_login(
                self.COLLECTION_USER_EMAIL, self.COLLECTION_USER_PASSWORD, ""
            )
        elif user == "submissions_user":
            if "dev.allizom" not in self.base_url:
                self.fxa_login(
                    self.SUBMISSIONS_USER_EMAIL,
                    self.SUBMISSIONS_USER_PASSWORD,
                    self.SUBMISSIONS_USER_KEY_STAGE,
                )
            else:
                self.fxa_login(
                    self.SUBMISSIONS_USER_EMAIL,
                    self.SUBMISSIONS_USER_PASSWORD,
                    self.SUBMISSIONS_USER_KEY_DEV,
                )
        elif user == "api_user":
            if "dev.allizom" not in self.base_url:
                self.fxa_login(
                    self.API_USER_EMAIL, self.API_USER_PASSWORD, self.API_USER_KEY_STAGE
                )
            else:
                self.fxa_login(
                    self.API_USER_EMAIL, self.API_USER_PASSWORD, self.API_USER_KEY_DEV
                )
        elif user == "staff_user":
            if "dev.allizom" not in self.base_url:
                self.fxa_login(
                    self.STAFF_USER_EMAIL,
                    self.STAFF_USER_PASSWORD,
                    self.STAFF_USER_KEY_STAGE,
                )
            else:
                self.fxa_login(
                    self.STAFF_USER_EMAIL,
                    self.STAFF_USER_PASSWORD,
                    self.STAFF_USER_KEY_DEV,
                )
        elif user == "restricted_user":
            self.fxa_login(
                self.RESTRICTED_USER_EMAIL, self.RESTRICTED_USER_PASSWORD, ""
            )
        elif user == "reviewer_user":
            self.fxa_login(
                self.REVIEWER_TOOLS_USER_EMAIL,
                self.REVIEWER_TOOLS_USER_PASSWORD,
                self.REVIEWER_TOOLS_USER_KEY
            )
        else:
            self.fxa_login(self.REGULAR_USER_EMAIL, self.REGULAR_USER_PASSWORD, "")

    def fxa_login(self, email, password, key):
        self.find_element(*self._email_locator).send_keys(email)
        self.find_element(*self._login_btn_locator).click()
        # sometimes, the login function fails on the 'continue_btn.click()' event with a TimeoutException
        # triggered by the built'in timeout of the 'click()' method;
        # however, the screenshot captured by the html report at test fail time shows that the click occurred
        # since the expected page has been loaded;
        # this seems to be a reoccurring issue in geckodriver as explained in
        # https://github.com/mozilla/geckodriver/issues/1608;
        # here, I'm capturing that TimeoutException and trying to push the script to continue to the next steps.
        try:
            continue_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "submit-btn"))
            )
            continue_btn.click()
        except TimeoutException as error:
            print(error.msg)
            pass
        print('The "click continue button" event occurred.')
        self.wait.until(
            EC.element_to_be_clickable(self._password_login),
            message=f"Password input field not displayed; "
            # f"FxA card header was {self.find_element(*self._login_card_header_locator).text}",
        )
        # print(
        #     f'The script should be on the password input screen here. We should see "Sign in" in the header.'
        #     f' The card  header title is "{self.find_element(*self._login_card_header_locator).text}"'
        # )
        self.find_element(*self._password_login).send_keys(password)
        # waits for the password to be filled in
        self.wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".password.empty")),
            message="There was no input added in the password field",
        )
        self.find_element(*self._login_btn_locator).click()
        # logic for 2fa enabled accounts
        if key != "":
            self.wait.until(EC.url_contains("signin_totp_code"))
            self.wait.until(EC.visibility_of_element_located(self._2fa_input_locator))
            time.sleep(30)
            totp = pyotp.TOTP(key)
            self.find_element(*self._2fa_input_locator).send_keys(totp.now())
            self.find_element(*self._confirm_2fa_button_locator).click()
            time.sleep(5)
            for max_retries in range(0, 2):
                if self.is_element_displayed(*self._error_2fa_code_locator):
                    time.sleep(500)
                    totp = pyotp.TOTP(key)
                    self.find_element(*self._2fa_input_locator).clear()
                    self.find_element(*self._2fa_input_locator).send_keys(totp.now())
                    self.find_element(*self._confirm_2fa_button_locator).click()
                else:
                    break

        # wait for transition between FxA page and AMO
        self.wait.until(
            EC.url_contains("addons"),
            message=f"AMO could not be loaded in {self.driver.current_url}. "
            f"Response status code was {requests.head(self.driver.current_url).status_code}",
        )

    def fxa_register(self):
        email = f"{reusables.get_random_string(10)}@restmail.net"
        password = reusables.get_random_string(12)
        self.find_element(*self._email_locator).send_keys(email)
        self.find_element(*self._login_btn_locator).click()
        # catching the geckodriver click() issue, in cae it happens here
        # issue - https://github.com/mozilla/geckodriver/issues/1608
        try:
            continue_btn = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "cta-primary cta-xl"))
            )
            continue_btn.click()
        except TimeoutException as error:
            print(error.msg)
            pass
        # verify that the fxa register form was opened
        time.sleep(5)
        self.find_element(*self._password_locator).send_keys(password)
        self.wait.until(
            EC.element_to_be_clickable(self._password_locator),
            message=f"Password input field not displayed; "
            f"FxA card header was {self.find_element(*self._login_card_header_locator).text}",
        )
        # self.find_element(*self._repeat_password_locator).send_keys(password)
        # self.find_element(*self._age_locator).send_keys(23)
        self.find_element(*self._login_btn_locator).click()
        # sleep to allow FxA to process the request and communicate with the email client
        time.sleep(10)
        verification_code = self.get_verification_code(email)
        self.find_element(*self._code_input_locator).send_keys(verification_code)
        self.find_element(*self._login_btn_locator).click()

    def get_verification_code(self, mail):
        request = requests.get(f"https://restmail.net/mail/{mail}", timeout=10)
        response = request.json()
        # creating a timed loop to address a possible communication delay between
        # FxA and restmail; this loop polls the endpoint for 20s to await a response
        # and exits if there was no response received in the given amount of time
        timeout_start = time.time()
        while time.time() < timeout_start + 20:
            if response:
                verification_code = [
                    key["headers"]["x-verify-short-code"] for key in response
                ]
                return verification_code
            elif not response:
                requests.get(f"https://restmail.net/mail/{mail}", timeout=10)
                print("Restmail did not receive an email from FxA")
        return self
