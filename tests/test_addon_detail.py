import pytest
import urllib.request

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.select import Select

from pages.desktop.details import Detail
from pages.desktop.users import User
from pages.desktop.reviews import Reviews


@pytest.mark.nondestructive
def test_extension_meta_card(selenium, base_url, variables):
    # Checks addon essential data (name, icon, author name, summary)
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert variables["detail_extension_name"] in addon.name
    assert addon.addon_icon.is_displayed()
    assert addon.authors.is_displayed()
    assert addon.summary.is_displayed()


@pytest.mark.nondestructive
def test_detail_author_links(selenium, base_url, variables):
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    # read the add-on author name and clicks on it
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    author = addon.authors.text
    addon.authors.click()
    # verify that the author profile page opens
    user = User(selenium, base_url).wait_for_page_to_load()
    assert author in user.user_display_name


@pytest.mark.nondestructive
def test_addon_detail_recommended_badge(selenium, base_url, variables):
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert addon.promoted_badge.is_displayed()
    assert "Recommended" in addon.promoted_badge_category
    # checks that the badge redirects to the correct sumo article
    addon.click_promoted_badge()
    assert "add-on-badges" in selenium.current_url


@pytest.mark.nondestructive
def test_addon_detail_by_firefox_badge(selenium, base_url, variables):
    extension = variables["by_firefox_addon"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert addon.promoted_badge.is_displayed()
    assert "By Firefox" in addon.promoted_badge_category
    # checks that the badge redirects to the correct sumo article
    addon.click_promoted_badge()
    assert "add-on-badges" in selenium.current_url


@pytest.mark.nondestructive
def test_non_promoted_addon(selenium, base_url, variables):
    extension = variables["experimental_addon"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    # check that the Promoted badge is not displayed
    with pytest.raises(NoSuchElementException):
        selenium.find_element_by_class_name("PromotedBadge-large")
    # checks the presence of an install warning
    assert addon.install_warning.is_displayed()
    assert variables["install_warning_message"] in addon.install_warning_message
    addon.click_install_warning_button()
    assert "add-on-badges" in selenium.current_url


@pytest.mark.nondestructive
def test_experimental_addon(selenium, base_url, variables):
    extension = variables["experimental_addon"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert addon.experimental_badge.is_displayed()


@pytest.mark.nondestructive
def test_lower_firefox_incompatibility(selenium, base_url, variables):
    extension = variables["lower_firefox_version"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert (
        "This add-on is not compatible with your version of Firefox."
        in addon.incompatibility_message
    )
    assert addon.button_state_disabled


@pytest.mark.nondestructive
def test_higher_firefox_incompatibility(selenium, base_url, variables):
    extension = variables["higher_firefox_version"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert (
        "This add-on requires a newer version of Firefox"
        in addon.incompatibility_message
    )
    assert addon.button_state_disabled


@pytest.mark.nondestructive
def test_platform_incompatibility(selenium, base_url, variables):
    extension = variables["incompatible_platform"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert (
        "This add-on is not available on your platform."
        in addon.incompatibility_message
    )
    assert addon.button_state_disabled


@pytest.mark.nondestructive
def test_addon_with_stats_summary(selenium, base_url, variables):
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # checks that a summary of users, reviews and star ratings are present
    assert addon.stats.stats_users_count > 0
    assert addon.stats.stats_reviews_count > 0
    assert addon.stats.addon_star_rating_stats.is_displayed()


@pytest.mark.nondestructive
def test_addon_without_stats_summary(selenium, base_url, variables):
    extension = variables["addon_without_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert "No Users" in addon.stats.no_user_stats
    assert "No Reviews" in addon.stats.no_reviews_stats
    assert "Not rated yet" in addon.stats.no_star_ratings


@pytest.mark.nondestructive
def test_stats_reviews_summary_click(selenium, base_url, variables):
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    stats_review_counts = addon.stats.stats_reviews_count
    # clicks on reviews stats link to open all reviews page
    reviews = addon.stats.stats_reviews_link()
    review_page_counts = reviews.reviews_title_count
    # checks that stats review numbers and all reviews page count match
    assert stats_review_counts == review_page_counts


@pytest.mark.nondestructive
def test_stats_rating_bars_summary(selenium, base_url, variables):
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # checks that there are 5 rating bars displayed, grouped by
    # ratings scores from 1 to 5 and tha rating counts are also
    # present for each bar - i.e. 5 elements in each category
    assert len(addon.stats.bar_grouped_ratings) == 5
    assert len(addon.stats.rating_bars) == 5
    assert len(addon.stats.bar_rating_counts) == 5


@pytest.mark.nondestructive
def test_click_stats_rating_bar(selenium, base_url, variables):
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # clicks on the first rating bar, verifies that all reviews page opens and
    # is filtered by the correct rating score, which is 5 stars for the first bar
    addon.stats.rating_bars[0].click()
    reviews = Reviews(selenium, base_url).wait_for_page_to_load()
    select = Select(reviews.filter_by_score)
    assert "Show only five-star reviews" in select.first_selected_option.text


@pytest.mark.nondestructive
def test_click_stats_bar_rating_counts(selenium, base_url, variables):
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # clicks on the second bar ratings count (number displayed on the right side of the bar)
    # verifies that all reviews page opens and is filtered by the correct rating score
    # which should be 4 stars in this case
    addon.stats.bar_rating_counts[1].click()
    reviews = Reviews(selenium, base_url).wait_for_page_to_load()
    select = Select(reviews.filter_by_score)
    assert "Show only four-star reviews" in select.first_selected_option.text


@pytest.mark.nondestructive
def test_click_stats_grouped_ratings(selenium, base_url, variables):
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # clicks on the grouped ratings number displayed left to a rating bar,
    # verifies that all reviews page opens and is filtered by the correct rating score
    addon.stats.bar_grouped_ratings[2].click()
    reviews = Reviews(selenium, base_url).wait_for_page_to_load()
    select = Select(reviews.filter_by_score)
    assert "Show only three-star reviews" in select.first_selected_option.text


@pytest.mark.nondestructive
def test_stats_rating_counts_compare(selenium, base_url, variables):
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # sums up the rating counts displayed next to each stats rating bar
    bar_count = sum([int(el.text) for el in addon.stats.bar_rating_counts])
    # reads the total number of reviews displayed in stats summary
    stats_count = addon.stats.stats_reviews_count
    assert bar_count == stats_count


@pytest.mark.nondestructive
def test_contribute_button(selenium, base_url, variables):
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert "Support this developer" in addon.contribute.contribute_card_header
    assert (
        variables["contribute_card_summary"] in addon.contribute.contribute_card_content
    )
    addon.contribute.click_contribute_button()
    # verifies that utm params are passed from AMO to the external contribute site
    wait = WebDriverWait(selenium, 10)
    wait.until(expected.url_contains(variables["contribute_utm_param"]))


@pytest.mark.nondestructive
def test_extension_permissions(selenium, base_url, variables):
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert "Permissions" in addon.permissions.permissions_card_header
    permissions = addon.permissions.permissions_list
    # checks that each permission has a corresponding icon and description
    for permission in permissions:
        assert permission.permission_icon.is_displayed()
        assert permission.permission_description.is_displayed()
    addon.permissions.click_permissions_button()
    addon.wait_for_current_url("permission-request")


@pytest.mark.nondestructive
def test_more_info_card_header(selenium, base_url, variables):
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert "More information" in addon.more_info.more_info_card_header


@pytest.mark.parametrize(
    "count, link", enumerate(["Homepage", "Support site", "Support Email"])
)
@pytest.mark.nondestructive
def test_more_info_support_links(selenium, base_url, variables, count, link):
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert link in addon.more_info.addon_support_links[count].text
    # excluding 'Support Email' since it doesn't open a new page when
    # clicked; this is a mailto link which is not handled by the browser
    if count != 2:
        addon.more_info.addon_support_links[count].click()
        # opens the homepage/support page provided by the developer
        addon.wait_for_current_url("ghostery.com")


@pytest.mark.nondestructive
def test_more_info_version_number(selenium, base_url, variables):
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.more_info.addon_version_number.is_displayed()


@pytest.mark.nondestructive
def test_more_info_addon_size(selenium, base_url, variables):
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.more_info.addon_size.is_displayed()
    more_info_size = addon.more_info.addon_size.text.split()[0].replace(" MB", "")
    # get the file URL and read its size - conversion from bytes to Mb is required
    file = urllib.request.urlopen(
        "https://addons.allizom.org/firefox/downloads/file/1097275/ghostery_privacy_ad_blocker-8.5.6-an+fx.xpi"
    )
    size = file.length / (1024 * 1024)
    # transforming the file size in two decimal format and comparing
    # with the size number displayed in the more info card
    assert "%.2f" % size == more_info_size


@pytest.mark.nondestructive
def test_more_info_addon_last_update(selenium, base_url, variables):
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.more_info.addon_last_update_date.is_displayed()


@pytest.mark.nondestructive
def test_more_info_external_license(selenium, base_url, variables):
    extension = variables["addon_without_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.more_info.addon_external_license()
    # checks that redirection to an external page happens
    assert variables["base_url"] not in selenium.current_url
