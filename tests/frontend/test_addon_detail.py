import time
import pytest
import urllib.request
import urllib.parse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.select import Select

from pages.desktop.frontend.details import Detail
from pages.desktop.frontend.search import Search
from pages.desktop.frontend.users import User
from pages.desktop.frontend.reviews import Reviews


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_extension_meta_card(selenium, base_url, variables):
    # Checks addon essential data (name, icon, author name, summary)
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert variables['detail_extension_name'] in addon.name
    assert addon.addon_icon.is_displayed()
    assert addon.authors.is_displayed()
    assert addon.summary.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_detail_author_links(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    # read the add-on author name and clicks on it
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    author = addon.authors.text
    addon.authors.click()
    # verify that the author profile page opens
    user = User(selenium, base_url).wait_for_page_to_load()
    assert author in user.user_display_name.text


@pytest.mark.nondestructive
def test_addon_detail_recommended_badge(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert addon.promoted_badge.is_displayed()
    assert 'Recommended' in addon.promoted_badge_category
    # checks that the badge redirects to the correct sumo article
    addon.click_promoted_badge()
    assert 'add-on-badges' in selenium.current_url


@pytest.mark.nondestructive
def test_addon_detail_by_firefox_badge(selenium, base_url, variables):
    extension = variables['by_firefox_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert addon.promoted_badge.is_displayed()
    assert 'By Firefox' in addon.promoted_badge_category
    # checks that the badge redirects to the correct sumo article
    addon.click_promoted_badge()
    assert 'add-on-badges' in selenium.current_url


@pytest.mark.nondestructive
def test_non_promoted_addon(selenium, base_url, variables):
    extension = variables['experimental_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    # check that the Promoted badge is not displayed
    with pytest.raises(NoSuchElementException):
        selenium.find_element_by_class_name('PromotedBadge-large')
    # checks the presence of an install warning
    assert addon.install_warning.is_displayed()
    assert variables['install_warning_message'] in addon.install_warning_message
    addon.click_install_warning_button()
    assert 'add-on-badges' in selenium.current_url


@pytest.mark.nondestructive
def test_experimental_addon(selenium, base_url, variables):
    extension = variables['experimental_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert addon.experimental_badge.is_displayed()


@pytest.mark.nondestructive
def test_lower_firefox_incompatibility(selenium, base_url, variables):
    extension = variables['lower_firefox_version']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert (
        'This add-on is not compatible with your version of Firefox.'
        in addon.incompatibility_message
    )
    assert addon.button_state_disabled


@pytest.mark.nondestructive
def test_higher_firefox_incompatibility(selenium, base_url, variables):
    extension = variables['higher_firefox_version']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert (
        'You need an updated version of Firefox for this extension'
        in addon.compatibility_banner.text
    )
    assert 'Download Firefox' in addon.get_firefox_button.text
    # clicks on the Download button and checks that the download Firefox page opens
    addon.get_firefox_button.click()
    addon.wait_for_current_url('/firefox/download/thanks/')


@pytest.mark.nondestructive
def test_platform_incompatibility(selenium, base_url, variables):
    extension = variables['incompatible_platform']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert (
        'This add-on is not available on your platform.'
        in addon.incompatibility_message
    )
    assert addon.button_state_disabled


@pytest.mark.nondestructive
def test_addon_with_stats_summary(selenium, base_url, variables):
    extension = variables['addon_with_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # checks that a summary of users, reviews and star ratings are present
    assert addon.stats.stats_users_count > 0
    assert addon.stats.stats_reviews_count > 0
    assert addon.stats.addon_star_rating_stats.is_displayed()


@pytest.mark.nondestructive
def test_addon_without_stats_summary(selenium, base_url, variables):
    extension = variables['addon_without_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert 'No Users' in addon.stats.no_user_stats
    assert 'No Reviews' in addon.stats.no_reviews_stats
    assert 'Not rated yet' in addon.stats.no_star_ratings


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_stats_reviews_summary_click(selenium, base_url, variables):
    extension = variables['addon_with_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    stats_review_counts = addon.stats.stats_reviews_count
    # clicks on reviews stats link to open all reviews page
    reviews = addon.stats.stats_reviews_link()
    review_page_counts = reviews.reviews_title_count
    # checks that stats review numbers and all reviews page count match
    assert stats_review_counts == review_page_counts


@pytest.mark.nondestructive
def test_stats_rating_bars_summary(selenium, base_url, variables):
    extension = variables['addon_with_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # checks that there are 5 rating bars displayed, grouped by
    # ratings scores from 1 to 5 and tha rating counts are also
    # present for each bar - i.e. 5 elements in each category
    assert len(addon.stats.bar_grouped_ratings) == 5
    assert len(addon.stats.rating_bars) == 5
    assert len(addon.stats.bar_rating_counts) == 5


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_click_stats_rating_bar(selenium, base_url, variables):
    extension = variables['addon_with_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # clicks on the first rating bar, verifies that all reviews page opens and
    # is filtered by the correct rating score, which is 5 stars for the first bar
    addon.stats.rating_bars[0].click()
    reviews = Reviews(selenium, base_url).wait_for_page_to_load()
    select = Select(reviews.filter_by_score)
    assert 'Show only five-star reviews' in select.first_selected_option.text


@pytest.mark.nondestructive
def test_click_stats_bar_rating_counts(selenium, base_url, variables):
    extension = variables['addon_with_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # clicks on the second bar ratings count (number displayed on the right side of the bar)
    # verifies that all reviews page opens and is filtered by the correct rating score
    # which should be 4 stars in this case
    addon.stats.bar_rating_counts[1].click()
    reviews = Reviews(selenium, base_url).wait_for_page_to_load()
    select = Select(reviews.filter_by_score)
    assert 'Show only four-star reviews' in select.first_selected_option.text


@pytest.mark.nondestructive
def test_click_stats_grouped_ratings(selenium, base_url, variables):
    extension = variables['addon_with_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # clicks on the grouped ratings number displayed left to a rating bar,
    # verifies that all reviews page opens and is filtered by the correct rating score
    addon.stats.bar_grouped_ratings[2].click()
    reviews = Reviews(selenium, base_url).wait_for_page_to_load()
    select = Select(reviews.filter_by_score)
    assert 'Show only three-star reviews' in select.first_selected_option.text


@pytest.mark.nondestructive
def test_stats_rating_counts_compare(selenium, base_url, variables):
    extension = variables['addon_with_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # sums up the rating counts displayed next to each stats rating bar
    bar_count = sum([int(el.text) for el in addon.stats.bar_rating_counts])
    # reads the total number of reviews displayed in stats summary
    stats_count = addon.stats.stats_reviews_count
    assert bar_count == stats_count


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_contribute_button(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert 'Support this developer' in addon.contribute.contribute_card_header
    assert (
        variables['contribute_card_summary'] in addon.contribute.contribute_card_content
    )
    addon.contribute.click_contribute_button()
    # verifies that utm params are passed from AMO to the external contribute site
    wait = WebDriverWait(selenium, 10)
    wait.until(expected.url_contains(variables['contribute_utm_param']))


@pytest.mark.nondestructive
def test_extension_permissions(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert 'Permissions' in addon.permissions.permissions_card_header
    permissions = addon.permissions.permissions_list
    # checks that each permission has a corresponding icon and description
    for permission in permissions:
        assert permission.permission_icon.is_displayed()
        assert permission.permission_description.is_displayed()
    addon.permissions.click_permissions_button()
    addon.wait_for_current_url('permission-request')


@pytest.mark.nondestructive
def test_more_info_card_header(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert 'More information' in addon.more_info.more_info_card_header


@pytest.mark.sanity
@pytest.mark.parametrize(
    'count, link', enumerate(['Homepage', 'Support site', 'Support Email'])
)
@pytest.mark.nondestructive
def test_more_info_support_links(selenium, base_url, variables, count, link):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert link in addon.more_info.addon_support_links[count].text
    # excluding 'Support Email' since it doesn't open a new page when
    # clicked; this is a mailto link which is not handled by the browser
    if count != 2:
        addon.more_info.addon_support_links[count].click()
        # opens the homepage/support page provided by the developer
        addon.wait_for_current_url(variables['support_site_link'])


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_more_info_version_number(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.more_info.addon_version_number.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_more_info_addon_size(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.more_info.addon_size.is_displayed()
    more_info_size = addon.more_info.addon_size.text.split()[0].replace(' MB', '')
    # get the file URL and read its size - conversion from bytes to Mb is required
    file = urllib.request.urlopen(addon.addon_xpi)
    size = file.length / (1024 * 1024)
    # transforming the file size in two decimal format and comparing
    # with the size number displayed in the more info card
    assert '%.2f' % size == more_info_size


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_more_info_addon_last_update(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.more_info.addon_last_update_date.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_more_info_related_categories(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # get the name of one of the categories related to this addon
    category_name = addon.more_info.addon_categories[0].text
    addon.more_info.addon_categories[0].click()
    # clicking on the category opens a search results page with addons that share the same category
    same_category_results = Search(selenium, base_url).wait_for_page_to_load()
    count = 0
    # checking that the search results do include the category of the initial addon
    # I think it's sufficient to cross-check for the first five add-on in the results list
    while count <= 4:
        same_category_results.result_list.click_search_result(count)
        category_name_from_search = [el.text for el in addon.more_info.addon_categories]
        assert category_name in category_name_from_search
        selenium.back()
        same_category_results.wait_for_page_to_load()
        count += 1


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_more_info_external_license(selenium, base_url, variables):
    extension = variables['addon_with_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.more_info.addon_external_license()
    # checks that redirection to an external page happens
    assert variables['base_url'] not in selenium.current_url


@pytest.mark.nondestructive
def test_more_info_custom_license(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # checks that the AMO custom license page opens and has the correct content
    custom_license = addon.more_info.addon_custom_license()
    assert (
        'Custom License for Ghostery - Privacy Ad Blocker'
        in custom_license.custom_licence_and_privacy_header
    )
    assert custom_license.custom_licence_and_privacy_text.is_displayed()
    assert custom_license.custom_licence_and_privacy_summary_card.is_displayed()


@pytest.mark.nondestructive
def test_more_info_privacy_policy(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    privacy = addon.more_info.addon_privacy_policy()
    # checks that the AMO privacy policy page opens and has the correct content
    assert (
        'Privacy policy for Ghostery - Privacy Ad Blocker'
        in privacy.custom_licence_and_privacy_header
    )
    assert privacy.custom_licence_and_privacy_text.is_displayed()
    assert privacy.custom_licence_and_privacy_summary_card.is_displayed()


@pytest.mark.nondestructive
def test_more_info_privacy_policy_missing(selenium, base_url, variables):
    extension = variables['addon_without_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    Detail(selenium, base_url).wait_for_page_to_load()
    with pytest.raises(NoSuchElementException):
        selenium.find_element_by_class_name('AddonMoreInfo-privacy-policy-link')
    print('The add-on does not have a Privacy Policy')


@pytest.mark.nondestructive
def test_more_info_eula(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    eula = addon.more_info.addon_eula()
    # checks that the AMO eula page opens and has the correct content
    assert (
        'End-User License Agreement for Ghostery - Privacy Ad Blocker'
        in eula.custom_licence_and_privacy_header
    )
    assert eula.custom_licence_and_privacy_text.is_displayed()
    assert eula.custom_licence_and_privacy_summary_card.is_displayed()


@pytest.mark.nondestructive
def test_more_info_eula_missing(selenium, base_url, variables):
    extension = variables['addon_without_stats']
    selenium.get(f'{base_url}/addon/{extension}')
    Detail(selenium, base_url).wait_for_page_to_load()
    with pytest.raises(NoSuchElementException):
        selenium.find_element_by_class_name('AddonMoreInfo-eula')
    print('The add-on does not have an End User License Agreement')


@pytest.mark.nondestructive
def test_compare_more_info_latest_version(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    more_info_version = addon.more_info.addon_version_number.text
    all_versions = addon.more_info.addon_versions()
    assert (
        'Ghostery - Privacy Ad Blocker version history'
        in all_versions.versions_page_header.text
    )
    # verifies that the version number displayed in the more info card
    # matches the latest version number present in all versions page
    latest_version = all_versions.latest_version_number
    assert more_info_version == latest_version


@pytest.mark.nondestructive
def test_more_info_addon_tags(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # get the name of one of the tags related to this addon
    tag_name = addon.more_info.addon_tags[0].text
    addon.more_info.addon_tags[0].click()
    # clicking on the tag opens a search results page with addons that share the same tag
    same_tag_results = Search(selenium, base_url).wait_for_page_to_load()
    # verifies that the results URL mention the tag name (encoded)
    assert f'/tag/{urllib.parse.quote(tag_name)}/' in selenium.current_url
    count = 0
    # checking that the first 5 search results do include the tag of the initial addon
    while count < 5:
        try:
            same_tag_results.result_list.click_search_result(count)
            # the 'click_search_result' function should already wait for the detail page to load
            # but I also want to check that the page switch occurred; helps with debugging test failures
            addon.wait_for_current_url('firefox/addon/')
            tag_name_from_search = [el.text for el in addon.more_info.addon_tags]
            assert tag_name in tag_name_from_search, f'for {addon.name}'
            selenium.back()
            same_tag_results.search_results_list_loaded(5)
        except IndexError:
            print('There were less than 5 results matching the selected tag')
            break
        count += 1


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_screenshot_viewer(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # clicks through each screenshot and verifies that the screenshot full size viewer is opened
    for preview in addon.screenshots.screenshot_preview:
        preview.click()
        time.sleep(1)
        # checks that the screenshot viewer has opened
        addon.screenshots.screenshot_full_view_displayed()
        addon.screenshots.close_screenshot_view()


@pytest.mark.nondestructive
def test_screenshot_ui_navigation(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.screenshots.screenshot_preview[0].click()
    time.sleep(1)
    # click on the right arrow to navigate to the next image
    addon.screenshots.go_to_next_screenshot()
    assert '2' in addon.screenshots.screenshot_counter
    # click on the left arrow to navigate to the previous image
    addon.screenshots.go_to_previous_screenshot()
    assert '1' in addon.screenshots.screenshot_counter


@pytest.mark.nondestructive
def test_screenshot_keyboard_navigation(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.screenshots.screenshot_preview[0].click()
    time.sleep(1)
    # send the right key to navigate to the next image
    addon.screenshots.right_key_for_next_screenshot()
    assert '2' in addon.screenshots.screenshot_counter
    # send the left key to navigate to the previous image
    addon.screenshots.left_key_for_previous_screenshot()
    assert '1' in addon.screenshots.screenshot_counter
    # send ESC to close the screenshot viewer
    addon.screenshots.esc_to_close_screenshot_viewer()


@pytest.mark.nondestructive
def test_add_to_collection_card(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # verifies that the Add to Collection card is present on the detail page
    assert 'Add to collection' in addon.add_to_collection.collections_card_header
    assert addon.add_to_collection.collections_select_field.is_displayed()


@pytest.mark.nondestructive
def test_release_notes(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert (
        f'Release notes for {addon.more_info.addon_version_number.text}'
        in addon.release_notes.release_notes_header
    )
    assert addon.release_notes.release_notes_text.is_displayed()


@pytest.mark.nondestructive
def test_more_addons_by_author_card(selenium, base_url, variables):
    extension = variables['experimental_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # verifies that the author name from the add-on summary card
    # is also present in the add-ons by same author card
    assert (
        f'More extensions by {addon.authors.text}'
        in addon.same_author_addons.addons_by_author_header
    )
    same_author_results = addon.same_author_addons.addons_by_author_results_list
    # checks that up to six addons by the same author are displayed in the card
    assert len(same_author_results) <= 6


@pytest.mark.nondestructive
def test_click_addon_in_more_addons_by_author(selenium, base_url, variables):
    extension = variables['experimental_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    result_name = addon.same_author_addons.addons_by_author_results_items[0].text
    # clicks on an addon present in the card and checks that the addon detail page is loaded
    addon.same_author_addons.addons_by_author_results_items[0].click()
    addon.wait_for_page_to_load()
    assert result_name in addon.name


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_addon_description(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert 'About this extension' in addon.description.addon_description_header
    assert addon.description.addon_description_text.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_addon_ratings_card(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert 'Rate your experience' in addon.ratings.ratings_card_header
    assert (
        variables['ratings_card_summary']
        in addon.ratings.ratings_card_summary
    )
    # checks that the login button is present in the ratings card
    # when the add-on detail page is viewed by unauthenticated users
    addon.ratings.rating_login_button.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_addon_recommendations(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    recommendations = addon.recommendations.addons_recommendations_results_list
    # verifies that the recommendations card shows up to 4 recommendations if available
    assert len(recommendations) <= 4


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_click_addon_recommendations(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    recommendation_name = addon.recommendations.recommendations_results_item[0].text
    # clicks on a recommendations and checks that the addon detail page is loaded
    addon.recommendations.recommendations_results_item[0].click()
    addon.wait_for_page_to_load()
    assert recommendation_name in addon.name


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_theme_detail_page(selenium, base_url, variables):
    extension = variables['theme_detail_page']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.themes.theme_preview.is_displayed()
    # checks that we display More themes from the same artist and that
    # each additional theme has its own preview from a total of 6
    assert (
        f'More themes by {addon.authors.text}'
        in addon.same_author_addons.addons_by_author_header
    )
    theme_by_same_artist = addon.same_author_addons.addons_by_author_results_list
    theme_by_same_artist_previews = addon.themes.more_themes_by_author_previews
    assert len(theme_by_same_artist) <= 6
    assert len(theme_by_same_artist) == len(theme_by_same_artist_previews)


@pytest.mark.nondestructive
def test_current_theme_not_in_more_by_artist_previews(selenium, base_url, variables):
    extension = variables['theme_detail_page']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # makes a record of the preview image source displayed first in the more themes by artist
    # card, clicks on the preview and verifies that the theme is no longer present in
    # the preview list since it is the currently opened theme detail page
    theme_preview = addon.themes.more_themes_by_author_previews[0].get_attribute('src')
    addon.themes.more_themes_by_author_previews[0].click()
    addon.wait_for_page_to_load()
    assert theme_preview not in addon.themes.preview_source
