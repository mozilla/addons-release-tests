"""A module where we customize waits that are not found in the predefined
selenium expected_conditions class"""


def url_not_contains(url):
    """An expectation for checking that the current url is not a specific value"""

    def _predicate(driver):
        return url not in driver.current_url

    return _predicate
