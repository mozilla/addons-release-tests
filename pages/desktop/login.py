

from selenium.webdriver.common.by import By

from pages.desktop.base import Base
import pytest_fxa


class Login(Base):

    #_email_locator = (By.NAME, 'email')
    _email_locator = (By.ID, 'email')
    #_continue_locator = (By.ID, 'submit-btn')
    _password_locator = (By.ID, 'password')
    _login_btn = (By.ID, 'login')

    def fxa_login(self, fxa_account):
        self.find_element(*self._email_locator).send_keys(fxa_account.email)
        # self.find_element(*self._continue_locator).click()
        self.find_element(*self._password_locator).send_keys(fxa_account.password)
        self.find_element(*self._login_btn).click()

