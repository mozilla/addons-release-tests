import os
import time

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.desktop.base import Base


class Login(Base):
    """The following variables need to be set as Environment Variables
     when running tests locally. These variables are also set in CircleCI's
    Project level Environment Variables and are picked up at runtime"""

    # 1. user that performs normal operations on the site, like writing add-on reviews
    REGULAR_USER_EMAIL = os.environ.get('REGULAR_USER_EMAIL')
    REGULAR_USER_PASSWORD = os.environ.get('REGULAR_USER_PASSWORD')
    # 2. user with elevated permissions that can perform special actions on the site
    ADMIN_USER_EMAIL = os.environ.get('ADMIN_USER_EMAIL')
    ADMIN_USER_PASSWORD = os.environ.get('ADMIN_USER_PASSWORD')
    # 3. user who has published add-ons on AMO
    DEVELOPER_EMAIL = os.environ.get('DEVELOPER_EMAIL')
    DEVELOPER_PASSWORD = os.environ.get('DEVELOPER_PASSWORD')
    # 4. user who re-creates accounts on AMO after having deleted them previously
    REUSABLE_USER_EMAIL = os.environ.get('REUSABLE_USER_EMAIL')
    REUSABLE_USER_PASSWORD = os.environ.get('REUSABLE_USER_PASSWORD')
    # 5. user used for the ratings tests
    RATING_USER_EMAIL = os.environ.get('RATING_USER_EMAIL')
    RATING_USER_PASSWORD = os.environ.get('RATING_USER_PASSWORD')

    _email_locator = (By.NAME, 'email')
    _continue_locator = (By.CSS_SELECTOR, '.button-row button')
    _password_locator = (By.ID, 'password')
    _login_btn_locator = (By.ID, 'submit-btn')
    _repeat_password_locator = (By.ID, 'vpassword')
    _age_locator = (By.ID, 'age')
    _code_input_locator = (By.CSS_SELECTOR, '.tooltip-below')
    _login_card_header_locator = (By.CSS_SELECTOR, '.card header h1')

    def account(self, user):
        if user == 'reusable_user':
            self.fxa_login(self.REUSABLE_USER_EMAIL, self.REUSABLE_USER_PASSWORD)
        elif user == 'admin':
            self.fxa_login(self.ADMIN_USER_EMAIL, self.ADMIN_USER_PASSWORD)
        elif user == 'developer':
            self.fxa_login(self.DEVELOPER_EMAIL, self.DEVELOPER_PASSWORD)
        elif user == 'rating_user':
            self.fxa_login(self.RATING_USER_EMAIL, self.RATING_USER_PASSWORD)
        else:
            self.fxa_login(self.REGULAR_USER_EMAIL, self.REGULAR_USER_PASSWORD)

    def fxa_login(self, email, password):
        self.find_element(*self._email_locator).send_keys(email)
        try:
            continue_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.button-row button'))
            )
            # time.sleep(2)
            continue_btn.click()
        except TimeoutException as e:
            print(e.msg)
            pass
        print(self.find_element(*self._login_card_header_locator).text)
        self.wait.until(
            EC.text_to_be_present_in_element(
                self._login_card_header_locator, 'Sign in'
            ),
            message=f'FxA card header was {self.find_element(*self._login_card_header_locator).text}',
        )
        print(self.find_element(*self._login_card_header_locator).text)
        self.find_element(*self._password_locator).send_keys(password)
        # waits for the password to be filled in
        self.wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, '.password.empty')),
            message='There was no input added in the password field',
        )
        self.find_element(*self._login_btn_locator).click()
