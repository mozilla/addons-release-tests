import pytest

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.details import Detail
from pages.desktop.reviews import Reviews


@pytest.mark.serial
@pytest.mark.nondestructive
def test_rating_with_text(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('regular_user')
    addon.ratings.rating_stars[3].click()
    # waits for the write a review form to be displayed
    addon.ratings.wait_for_rating_form()
    addon.ratings.write_a_review.click()
    review_text = 'first review text'
    addon.ratings.review_text_input(review_text)
    addon.ratings.submit_review()
    # verifies that the input review text was saved
    assert addon.ratings.written_review.text == review_text
    # checks that the review posting time is recorded
    assert 'a few seconds ago' in addon.ratings.review_permalink.text


@pytest.mark.serial
@pytest.mark.nondestructive
def test_user_review_permalink(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('regular_user')
    # click on the review permalink (post date) and check that the All reviews page opens
    # with the posted user review on top (i.e. the user display name is in the All Reviews page title)
    addon.ratings.review_permalink.click()
    reviews = Reviews(selenium, base_url).wait_for_page_to_load()
    assert 'regular_user' in reviews.user_review_permalink


@pytest.mark.serial
@pytest.mark.nondestructive
def test_edit_review(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('regular_user')
    addon.ratings.edit_review.click()
    edited_review_text = ' edited review text'
    addon.ratings.review_text_input(edited_review_text)
    # updates the review text and verifies that the changes are saved
    addon.ratings.submit_review()
    assert edited_review_text in addon.ratings.written_review.text


@pytest.mark.serial
@pytest.mark.nondestructive
def test_cancel_edit_review(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('regular_user')
    addon.ratings.edit_review.click()
    # cancel the edit review from and check that the form is no longer displayed
    addon.ratings.cancel_review.click()
    with pytest.raises(NoSuchElementException):
        selenium.find_element_by_css_selector(
            '.AddonReviewManager .DismissibleTextForm-dismiss'
        )


@pytest.mark.serial
@pytest.mark.nondestructive
def test_cancel_delete_review(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('regular_user')
    addon.ratings.delete_review.click()
    # opt for the option to keep the review instead confirming to delete it
    # and verify that the review body is still displayed after that
    addon.ratings.keep_review.click()
    assert addon.ratings.written_review.is_displayed()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_delete_review(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('regular_user')
    addon.ratings.delete_review.click()
    addon.ratings.delete_confirm_button()
    # checks that the review text is no longer displayed
    with pytest.raises(NoSuchElementException):
        selenium.find_element_by_css_selector('.UserReview-body')


@pytest.mark.serial
@pytest.mark.nondestructive
def test_rating_without_text(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('regular_user')
    # total number of reviews in stats card before leaving a new rating
    prior_rating_count = addon.stats.stats_reviews_count
    # number of ratings with a score of 5 stars before leaving a new rating
    prior_bar_rating_count = int(addon.stats.bar_rating_counts[0].text)
    # post a 5 star rating score and check that 5 stars are highlighted
    addon.ratings.rating_stars[4].click()
    assert len(addon.ratings.selected_star_highlight) == 5
    addon.ratings.wait_for_rating_form()
    # number of reviews in stats card after leaving a rating
    new_rating_count = addon.stats.stats_reviews_count
    new_bar_rating_count = int(addon.stats.bar_rating_counts[0].text)
    assert new_rating_count == prior_rating_count + 1
    assert new_bar_rating_count == prior_bar_rating_count + 1


@pytest.mark.serial
@pytest.mark.nondestructive
def test_edit_star_rating(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('regular_user')
    # checks the rating score before selecting a different star rating
    assert len(addon.ratings.selected_star_highlight) == 5
    addon.ratings.rating_stars[3].click()
    # verifies that the new score is reflected by the number of highlighted stars
    assert len(addon.ratings.selected_star_highlight) == 4


@pytest.mark.serial
@pytest.mark.nondestructive
def test_link_to_all_reviews(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('regular_user')
    reviews_link_count = addon.ratings.all_reviews_link_rating_count
    # click on the ratings card link to open the All Reviews page
    reviews = addon.ratings.all_reviews_link()
    # check that the ratings card review counts and All Reviews counts are matching
    assert reviews_link_count == reviews.reviews_title_count


@pytest.mark.serial
@pytest.mark.nondestructive
def test_delete_rating(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('regular_user')
    addon.ratings.delete_rating_link.click()
    addon.ratings.delete_confirm_button()
    # verifies that rating stars are no longer full after deleting the rating
    WebDriverWait(selenium, 10).until(
        EC.invisibility_of_element_located(addon.ratings.selected_star_highlight)
    )
