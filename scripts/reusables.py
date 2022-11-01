"""A module where we store reusable methods and various scripts
 that can help with our test functions"""

import datetime
import random
import string


def scroll_into_view(driver, element):
    """This method adds page scrolling to accompany tests
    that use ActionChains.move_to_element but run into a
    MoveTargetOutOfBoundsException in Firefox"""
    x = element.location['x']
    y = element.location['y']
    scroll_by_coord = 'window.scrollTo(%s,%s);' % (x, y)
    scroll = 'window.scrollBy(0, -120);'
    driver.execute_script(scroll_by_coord)
    driver.execute_script(scroll)


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def current_date():
    """Getting the current date in string format"""
    today = datetime.datetime.today()
    time = today.strftime('%b %#d, %Y')
    return time


def convert_bytes(size):
    """Used for converting addon file sizes from bytes (as returned by the 'file.length' property) to units
      from on AMO (usually KB or MB) for the purpose of comparing that AMO is showing the correct file size"""
    for x in ['bytes', 'KB', 'MB']:
        if size < 1024.0:
            return "%3.2f %s" % (size, x)
        size /= 1024.0
    return size
