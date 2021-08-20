"""A class where we customize waits that are not found in the predefined
selenium expected_conditions class"""


class url_not_contins(object):
    def __init__(self, url):
        self.url = url

    def __call__(self, driver):
        return self.url not in driver.current_url
