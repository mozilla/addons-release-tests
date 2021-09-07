"""A module where we customize waits that are not found in the predefined
selenium expected_conditions class"""


class url_not_contins(object):
    def __init__(self, url):
        self.url = url

    def __call__(self, driver):
        return self.url not in driver.current_url


class check_value_inequality(object):
    def __init__(self, first_value, second_value):
        self.first_value = first_value
        self.second_value = second_value

    def __call__(self, ignored):
        return self.first_value != self.second_value
