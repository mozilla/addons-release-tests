---
name: selenium-test-generator
description: Use this skill when the user wants to create, extend, refactor, or organize automated UI tests using Python, Selenium, pytest, Page Object Model, PyCharm, and Firefox Nightly.
---

# Selenium Test Generator

## Main goal

Generate clean, maintainable automated UI tests for an existing Selenium project.

## Assumptions

Unless the user says otherwise:

- The project uses Python.
- The test runner is pytest.
- The browser is Firefox Nightly.
- The IDE is PyCharm.
- The framework uses Selenium WebDriver.
- The preferred structure is Page Object Model.
- Tests should be compatible with existing fixtures from `conftest.py`.

## Rules

Always follow these rules:

1. Do not use `time.sleep()`.
2. Use explicit waits with `WebDriverWait`.
3. Prefer CSS selectors over XPath when possible.
4. Use XPath only when CSS cannot express the locator clearly.
5. Keep assertions inside test files, not page objects.
6. Keep Selenium interactions inside page objects.
7. Use meaningful method names.
8. Make tests readable and business-focused.
9. Do not hardcode credentials directly in tests.
10. Use fixtures for driver, base URL, credentials, and environment configuration.
11. Make the code Firefox-compatible.
12. Assume tests may run against dev and stage environments.

## Expected output format

When creating a new test flow, output:

1. Suggested file structure
2. Page object class
3. Test class or test function
4. Required fixture changes, if needed
5. Run command
6. Notes about assumptions or missing details

## Page object style

Use this style:

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    _email_input = (By.CSS_SELECTOR, "[data-testid='email']")
    _password_input = (By.CSS_SELECTOR, "[data-testid='password']")
    _submit_button = (By.CSS_SELECTOR, "button[type='submit']")

    def enter_email(self, email):
        element = self.wait.until(EC.visibility_of_element_located(self._email_input))
        element.clear()
        element.send_keys(email)

    def enter_password(self, password):
        element = self.wait.until(EC.visibility_of_element_located(self._password_input))
        element.clear()
        element.send_keys(password)

    def submit(self):
        self.wait.until(EC.element_to_be_clickable(self._submit_button)).click()

    def login(self, email, password):
        self.enter_email(email)
        self.enter_password(password)
        self.submit()