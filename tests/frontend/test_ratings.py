import pytest

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.frontend.details import Detail
from pages.desktop.frontend.reviews import Reviews


@pytest.mark.serial
@pytest.mark.nondestructive
def test_rating_with_text(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('rating_user')
    addon.ratings.rating_stars[3].click()
    # waits for the write a review form to be displayed
    addon.ratings.wait_for_rating_form()
    addon.ratings.write_a_review.click()
    review_text = variables['initial_text_input']
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
    addon.login('rating_user')
    # click on the review permalink (post date) and check that the All reviews page opens
    # with the posted user review on top (i.e. the user display name is in the All Reviews page title)
    addon.ratings.review_permalink.click()
    reviews = Reviews(selenium, base_url).wait_for_page_to_load()
    assert 'rating_user' in reviews.user_review_permalink


@pytest.mark.serial
@pytest.mark.nondestructive
def test_edit_review(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('rating_user')
    addon.ratings.edit_review.click()
    edited_review_text = variables['edited_text_input']
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
    addon.login('rating_user')
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
    addon.login('rating_user')
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
    addon.login('rating_user')
    addon.ratings.delete_review.click()
    addon.ratings.click_delete_confirm_button()
    # checks that the review text is no longer displayed
    with pytest.raises(NoSuchElementException):
        selenium.find_element_by_css_selector('.UserReview-body')


@pytest.mark.serial
@pytest.mark.nondestructive
def test_rating_without_text(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('rating_user')
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
    addon.login('rating_user')
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
    addon.login('rating_user')
    reviews_link_count = addon.ratings.all_reviews_link_rating_count
    # click on the ratings card link to open the All Reviews page
    reviews = addon.ratings.click_all_reviews_link()
    # check that the ratings card review counts and All Reviews counts are matching
    assert reviews_link_count == reviews.reviews_title_count


@pytest.mark.serial
@pytest.mark.nondestructive
def test_delete_rating(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('rating_user')
    addon.ratings.delete_rating_link.click()
    addon.ratings.click_delete_confirm_button()
    # verifies that rating stars are no longer full after deleting the rating
    WebDriverWait(selenium, 10).until(
        EC.invisibility_of_element_located(addon.ratings.selected_star_highlight)
    )


@pytest.mark.serial
@pytest.mark.nondestructive
def test_all_reviews_page_items(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    reviews = addon.ratings.click_all_reviews_link()
    assert reviews.addon_summary_card.is_displayed()
    for review in reviews.review_items:
        assert review.rating_stars.is_displayed()
        assert review.rating_user.is_displayed()
        assert review.posting_date.is_displayed()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_filter_reviews_by_score(selenium, base_url, variables):
    extension = variables['all_scores_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    reviews = addon.ratings.click_all_reviews_link()
    select = Select(reviews.filter_by_score)
    count = 1
    # selecting rating score filters from 1 to 5, verifying that the reviews card
    # header counts reflect the number of reviews available for that rating score
    # and that the ratings stars for each review reflect the selected score
    while count < 6:
        select.select_by_value(str(count))
        # waiting for the reviews page to be refreshed
        reviews.wait_for_page_to_load()
        assert reviews.reviews_title_count == len(reviews.reviews_list)
        for stars in reviews.review_items:
            assert len(stars.selected_star) == count
        count += 1


@pytest.mark.serial
@pytest.mark.nondestructive
def test_filter_reviews_from_rating_bars(selenium, base_url, variables):
    extension = variables['all_scores_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    reviews = addon.ratings.click_all_reviews_link()
    count = 0
    # sort reviews based on score by clicking on the ratings bars present
    # in the AddonSummaryCard; verify that the correct score is displayed
    # in the reviews card header and in the rating stars associated to each review
    while count < 5:
        reviews.score_bars[count].click()
        # waiting for the reviews page to be refreshed
        reviews.wait_for_page_to_load()
        assert reviews.reviews_title_count == len(reviews.reviews_list)
        for stars in reviews.review_items:
            assert len(stars.selected_star) == int(reviews.bar_rating_score[count].text)
        count += 1


@pytest.mark.serial
@pytest.mark.nondestructive
def test_flag_review_action(selenium, base_url, variables):
    extension = variables['all_scores_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('rating_user')
    reviews = addon.ratings.click_all_reviews_link()
    flag = reviews.review_items
    # the 'Flag' menu is displayed only for reviews with text
    # iterating through the list of reviews until a review with text is found
    count = 0
    while count <= len(reviews.reviews_list):
        if len(flag[count].review_body) > 0:
            flag[count].click_flag_review()
            # choosing the option to flag the review for spam
            assert (
                variables['review_flag_spam'] in flag[count].flag_review_option[0].text
            )
            flag[count].select_flag_option(0)
            assert (
                variables['review_flagged_for_spam']
                in flag[count].flag_review_success_text[0].text
            )
            break
        else:
            count += 1


@pytest.mark.serial
@pytest.mark.nondestructive
def test_flag_missing_for_empty_review(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    reviews = addon.ratings.click_all_reviews_link()
    # checks that each review without text doesn't have the Flag button
    for user_review in reviews.review_items:
        if len(user_review.review_body) == 0:
            with pytest.raises(NoSuchElementException):
                user_review.find_element(By.CSS_SELECTOR, '.FlagReviewMenu-menu')


@pytest.mark.serial
@pytest.mark.nondestructive
def test_flag_review_requires_login(selenium, base_url, variables):
    extension = variables['all_scores_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    reviews = addon.ratings.click_all_reviews_link()
    review_item = reviews.review_items
    # the 'Flag' menu is displayed only for reviews with text
    # iterating through the list of reviews until a review with text is found
    count = 0
    while count <= len(reviews.reviews_list):
        if len(review_item[count].review_body) > 0:
            review_item[count].click_flag_review()
            assert review_item[count].flag_review_login_button.is_displayed()
            break
        else:
            count += 1


@pytest.mark.serial
@pytest.mark.nondestructive
def test_flag_review_menu_options(selenium, base_url, variables):
    extension = variables['all_scores_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('rating_user')
    reviews = addon.ratings.click_all_reviews_link()
    flag = reviews.review_items
    count = 0
    while count <= len(reviews.reviews_list):
        if len(flag[count].review_body) > 0:
            flag[count].click_flag_review()
            # verifies that the following 3 report options are available in the flag menu
            assert (
                variables['review_flag_spam'] in flag[count].flag_review_option[0].text
            )
            assert (
                variables['review_flag_language']
                in flag[count].flag_review_option[1].text
            )
            assert (
                variables['review_flag_bug'] in flag[count].flag_review_option[2].text
            )
            break
        else:
            count += 1


@pytest.mark.serial
@pytest.mark.nondestructive
def test_write_review_in_all_reviews_page(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('rating_user')
    # post a rating on the detail page
    addon.ratings.rating_stars[4].click()
    # waits for the rating to be properly recorded
    addon.ratings.wait_for_rating_form()
    # navigate to the All reviews page to write your review
    reviews = addon.ratings.click_all_reviews_link()
    addon.ratings.write_a_review.click()
    review_text = variables['initial_text_input']
    addon.ratings.review_text_input(review_text)
    addon.ratings.submit_review()
    assert reviews.review_items[0].review_body == review_text


@pytest.mark.serial
@pytest.mark.nondestructive
def test_edit_review_in_all_reviews_page(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('rating_user')
    reviews = addon.ratings.click_all_reviews_link()
    addon.ratings.edit_review.click()
    # edit the previous rating in All reviews page and verify that the score is updated
    reviews.edit_review_score[3].click()
    assert len(reviews.selected_score_highlight) == 4
    # update the written review text in All reviews page
    edited_review_text = variables['edited_text_input']
    addon.ratings.review_text_input(edited_review_text)
    addon.ratings.submit_review()
    assert edited_review_text in reviews.review_items[0].review_body


@pytest.mark.serial
@pytest.mark.nondestructive
def test_delete_review_in_all_reviews_page(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('rating_user')
    reviews = addon.ratings.click_all_reviews_link()
    review_text = reviews.review_items[0].review_body
    reviews_count = reviews.reviews_title_count
    addon.ratings.delete_review.click()
    reviews.review_items[0].click_confirm_delete_button()
    # waits until the reviews count in the list header decreases by 1
    WebDriverWait(selenium, 10).until(
        EC.text_to_be_present_in_element(
            (By.CLASS_NAME, 'AddonReviewList-reviewCount'), f'{reviews_count - 1}'
        )
    )
    # checks that the review is no longer found in the list of available reviews
    for review in reviews.review_items:
        assert review_text not in review.review_body


@pytest.mark.serial
@pytest.mark.nondestructive
def test_developer_reply_to_review(selenium, base_url, variables):
    extension = variables['dev_reply_review']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('developer')
    reviews = addon.ratings.click_all_reviews_link()
    reviews.review_items[0].click_reply_to_review()
    reply_text = variables['initial_text_input']
    reviews.review_items[0].reply_text_input(reply_text)
    reviews.review_items[0].publish_reply()
    assert 'Developer response' in reviews.review_items[0].dev_reply_header.text
    assert reply_text == reviews.review_items[0].posted_reply_text


@pytest.mark.serial
@pytest.mark.nondestructive
def test_edit_developer_reply_to_review(selenium, base_url, variables):
    extension = variables['dev_reply_review']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('developer')
    reviews = addon.ratings.click_all_reviews_link()
    edited_reply = variables['edited_text_input']
    addon.ratings.edit_review.click()
    reviews.review_items[0].reply_text_input(edited_reply)
    reviews.review_items[0].publish_reply()
    assert edited_reply in reviews.review_items[0].posted_reply_text


@pytest.mark.serial
@pytest.mark.nondestructive
def test_delete_developer_reply_to_review(selenium, base_url, variables):
    extension = variables['dev_reply_review']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('developer')
    reviews = addon.ratings.click_all_reviews_link()
    addon.ratings.delete_review.click()
    reviews.review_items[0].click_confirm_delete_button()
    # verifies that the Developer reply section is no longer displayed
    WebDriverWait(selenium, 10).until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, '.AddonReviewCard-reply .ShowMoreCard-contents > div')
        )
    )
