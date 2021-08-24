"""A module where we store reusable methods and various scripts
 that can help with our test functions"""


def scroll_into_view(driver, element):
    """This method adds page scrolling to accompany tests
    that use ActionChains.move_to_element but run into a
    MoveTargetOutOfBoundsException in Firefox"""
    x = element.location['x']
    y = element.location['y']
    scroll_by_coord = 'window.scrollTo(%s,%s);' % (
        x,
        y
    )
    scroll = 'window.scrollBy(0, -120);'
    driver.execute_script(scroll_by_coord)
    driver.execute_script(scroll)
