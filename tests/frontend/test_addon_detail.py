import time
import urllib.request
import urllib.parse
import pytest
import requests

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from pages.desktop.frontend.details import Detail
from pages.desktop.frontend.search import Search
from pages.desktop.frontend.static_pages import StaticPages
from pages.desktop.frontend.users import User
from pages.desktop.frontend.reviews import Reviews
from pages.desktop.frontend.versions import Versions
from scripts import reusables

@pytest.mark.sanity
@pytest.mark.nondestructive
def test_extension_meta_card_tc_id_c392798(selenium, base_url, variables):
    """Checks addon essential data (name, icon, author name, summary)"""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert variables["detail_extension_name"] in addon.name
    assert addon.addon_icon.is_displayed()
    assert addon.authors.is_displayed()
    assert addon.summary.is_displayed()

@pytest.mark.sanity
@pytest.mark.nondestructive
def test_detail_author_links(selenium, base_url, variables):
    """Tests that the author's links are present and correct on the detail page."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    # read the add-on author name and clicks on it
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    author = addon.authors.text
    addon.authors.click()
    # verify that the author profile page opens
    user = User(selenium, base_url).wait_for_page_to_load()
    assert author in user.user_display_name.text

@pytest.mark.nondestructive
def test_addon_detail_recommended_badge(selenium, base_url, variables):
    """Tests that the recommended badge appears on the add-on detail page."""
    extension = variables["detail_extension_recommended_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert addon.promoted_badge.is_displayed()
    assert "Recommended" in addon.promoted_badge_category
    # checks that the badge redirects to the correct sumo article
    addon.click_promoted_badge()
    assert "add-on-badges" in selenium.current_url

@pytest.mark.nondestructive
def test_addon_detail_by_firefox_badge(selenium, base_url, variables):
    """Tests that the 'By Firefox' badge is displayed for official add-ons."""
    extension = variables["detail_extension_by_firefox_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert addon.by_firefox_badge.is_displayed()
    assert "By Firefox" in addon.by_firefox_label
    # checks that the badge redirects to the correct sumo article
    addon.click_promoted_badge()
    assert "add-on-badges" in selenium.current_url

@pytest.mark.nondestructive
def test_non_promoted_addon(selenium, base_url, variables):
    """Tests behavior for a non-promoted add-on."""
    extension = variables["experimental_addon"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    # check that the Promoted badge is not displayed
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CLASS_NAME, "PromotedBadge-large")
    # checks the presence of an install warning
    assert addon.install_warning.is_displayed()
    assert variables["install_warning_message"] in addon.install_warning_message
    addon.click_install_warning_button()
    assert "add-on-badges" in selenium.current_url


@pytest.mark.nondestructive
def test_experimental_addon(selenium, base_url, variables):
    """Tests how an experimental add-on is displayed or handled."""
    extension = variables["experimental_addon"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert addon.experimental_badge.is_displayed()

@pytest.mark.nondestructive
def test_invisible_addon(selenium, base_url, variables):
    """Verify the response for an invisible addon detail page when viewed
    with regular non-authorized users vs authorized users"""
    extension = variables["invisible_addon_detail"]
    selenium.get(f"{base_url}/addon/{extension}")
    page = StaticPages(selenium, base_url).wait_for_page_to_load()
    # for regular users detail pages should not be available, hence 404 page
    assert page.not_found_page.is_displayed()
    # login with the addon developer who should have access to the detail page
    page.login("developer")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert (
        "This is not a public listing. You are only seeing it because of elevated permissions."
        in addon.non_public_addon_notice.text
    )

@pytest.mark.nondestructive
def test_access_addon_by_guid(selenium, base_url, variables):
    """Access an addon detail page by its guid"""
    extension = variables["addon_detail_guid"]
    selenium.get(f"{base_url}/addon/{extension}") # pylint: disable=missing-timeout
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # making sure that the page doesn't return a 404
    response = requests.get(selenium.current_url, timeout=10)
    assert (
        response.status_code == 200
    ), f'Actual status code for "{selenium.current_url}" was "{response.status_code}"'
    assert addon.summary.is_displayed()

@pytest.mark.nondestructive
def test_access_addon_by_id(selenium, base_url, variables):
    """Access an addon detail page by its internal AMO id"""
    extension = variables["addon_detail_id"]
    selenium.get(f"{base_url}/addon/{extension}") # pylint: disable=missing-timeout
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # making sure that the page doesn't return a 404
    response = requests.get(selenium.current_url, timeout=10)
    assert (
        response.status_code == 200
    ), f'Actual status code for "{selenium.current_url}" was "{response.status_code}"'
    assert addon.summary.is_displayed()

@pytest.mark.nondestructive
def test_access_addon_by_unicode_slug(selenium, base_url, variables):
    """Access an addon detail page with a unicode slug"""
    extension = variables["addon_unicode_slug"]
    selenium.get(f"{base_url}/addon/{extension}") # pylint: disable=missing-timeout
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # making sure that the page doesn't return a 404
    response = requests.get(selenium.current_url, timeout=10)
    assert (
        response.status_code == 200
    ), f'Actual status code for "{selenium.current_url}" was "{response.status_code}"'
    assert addon.summary.is_displayed()


@pytest.mark.nondestructive
def test_lower_firefox_incompatibility(selenium, base_url, variables):
    """Tests behavior when an add-on is incompatible with lower Firefox versions."""
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
    """Tests behavior when an add-on is incompatible with higher Firefox versions."""
    extension = variables["higher_firefox_version"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert (
        "Download the new Firefox and get the extension"
        in addon.compatibility_banner.text
    )
    assert (
        "Download the new Firefox and get the extension"
        in addon.get_firefox_button.text
    )
    # clicks on the Download button and checks that the download Firefox page opens
    addon.get_firefox_button.click()
    addon.wait_for_current_url("/firefox/download/thanks/")


@pytest.mark.nondestructive
def test_platform_incompatibility_tc_id_c4453(selenium, base_url, variables):
    """Tests display and behavior for platform-incompatible add-ons."""
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
    """Tests display of stats summary for an add-on that has data."""
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # checks that a summary of users, reviews and star ratings are present
    assert addon.stats.stats_users_count > 0
    assert addon.stats.stats_reviews_count > 0
    assert addon.stats.addon_star_rating_stats.is_displayed()


@pytest.mark.nondestructive
def test_addon_without_stats_summary(selenium, base_url, variables):
    """Tests behavior when an add-on has no stats summary available."""
    extension = variables["addon_without_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert "No Users" in addon.stats.no_user_stats
    assert "0 (0 reviews)" in addon.stats.no_reviews_stats
    assert "No reviews yet" in addon.stats.no_star_ratings


@pytest.mark.sanity
@pytest.mark.nondestructive
@pytest.mark.skip(reason="update assert")
def test_stats_reviews_summary_click(selenium, base_url, variables):
    """Tests clicking on the reviews summary in stats."""
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
    """Tests that rating bars summary is displayed in stats section."""
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
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
    """Tests clicking on a specific rating bar in the stats."""
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
    """Tests the rating counts when a stats bar is clicked."""
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
    """Tests grouped ratings behavior when clicked."""
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
    """Tests comparison of rating counts between different add-ons or versions."""
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # sums up the rating counts displayed next to each stats rating bar
    bar_count = sum([int(el.text) for el in addon.stats.bar_rating_counts])
    # reads the total number of reviews displayed in stats summary
    stats_count = addon.stats.stats_reviews_count
    assert bar_count == stats_count


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_contribute_button_tc_id_c4402(selenium, base_url, variables):
    """Tests visibility and behavior of the contribute button."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert "Support this developer" in addon.contribute.contribute_card_header
    assert (
        variables["contribute_card_summary"] in addon.contribute.contribute_card_content
    )
    assert addon.contribute.contribute_button_heart_icon.is_displayed()
    assert "Contribute now" in addon.contribute.contribute_button_text
    addon.contribute.click_contribute_button()
    # verifies that utm params are passed from AMO to the external contribute site
    wait = WebDriverWait(selenium, 10)
    wait.until(expected.url_contains(variables["contribute_utm_param"]))


@pytest.mark.nondestructive
def test_extension_permissions_tc_id_c139966(selenium, base_url, variables):
    """Tests that extension permissions are displayed correctly."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url)
    assert "Permissions" in addon.permissions.permissions_card_header
    permissions = addon.permissions.permissions_list
    # checks that each permission has a corresponding icon and description
    for permission in permissions:
        # assert permission.permission_icon.is_displayed()
        assert permission.permission_description.is_displayed()
    assert "Learn more" in addon.permissions.permissions_learn_more_button
    # assert addon.permissions.permissions_learn_more_button_icon.is_displayed()
    # icon permission was removed
    addon.permissions.click_permissions_button()
    addon.wait_for_current_url("permission-request")


@pytest.mark.nondestructive
def test_more_info_card_header(selenium, base_url, variables):
    """Tests the header of the 'More Info' card on the detail page."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert "More information" in addon.more_info.more_info_card_header


@pytest.mark.sanity
@pytest.mark.parametrize(
    "count, link", enumerate(["Homepage", "Support site", "Support Email"])
)
@pytest.mark.nondestructive
def test_more_info_support_links(selenium, base_url, variables, count, link):
    """Tests the support links under the 'More Info' section."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert link in addon.more_info.addon_support_links[count].text
    # excluding 'Support Email' since it doesn't open a new page when
    # clicked; this is a mailto link which is not handled by the browser
    if count != 2:
        addon.more_info.addon_support_links[count].click()
        # opens the homepage/support page provided by the developer
        addon.wait_for_current_url(variables["support_site_link"])


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_more_info_version_number(selenium, base_url, variables):
    """Tests that the correct version number is displayed in 'More Info'."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.more_info.addon_version_number.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
@pytest.mark.skip
def test_more_info_addon_size(selenium, base_url, variables):
    """Tests the add-on size value in the 'More Info' section."""
    extension = variables["addon_size_extension"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.more_info.addon_size.is_displayed()
    more_info_size = addon.more_info.addon_size.text
    # get the file URL and read its size
    file = urllib.request.urlopen(addon.addon_xpi)
    # convert the size returned by the file.length from bytes to the unit displayed on AMO
    size = reusables.convert_bytes(file.length/10)
    assert size == more_info_size


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_more_info_addon_last_update(selenium, base_url, variables):
    """Tests that the last updated date is shown in 'More Info'."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.more_info.addon_last_update_date.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_more_info_related_categories(selenium, base_url, variables):
    """Tests that related categories are listed under 'More Info'."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
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
    """Tests that an external license link is displayed if available."""
    extension = variables["addon_with_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.more_info.click_addon_external_license()
    # checks that redirection to an external page happens
    assert variables["base_url"] not in selenium.current_url


@pytest.mark.parametrize(
    "extension, license_name, license_link",
    [
        (
            "mpl-2-0",
            "Mozilla Public License 2.0",
            "https://www.mozilla.org/en-US/MPL/2.0/",
        ),
        (
            "gnu-general-2-0",
            "GNU General Public License v2.0 only",
            "https://spdx.org/licenses/GPL-2.0-only.html",
        ),
        (
            "gnu-general-3-0",
            "GNU General Public License v3.0",
            "https://spdx.org/licenses/GPL-3.0-only.html",
        ),
        (
            "gnu-library-2-1",
            "GNU Lesser General Public License v2.1",
            "https://spdx.org/licenses/LGPL-2.1-only.html",
        ),
        (
            "gnu-library-3-0",
            "GNU Lesser General Public License v3.0",
            "https://spdx.org/licenses/LGPL-3.0-only.html",
        ),
        (
            "mit-license",
            "MIT License",
            "https://spdx.org/licenses/MIT.html",
        ),
        (
            "bsd-license",
            "BSD 2-Clause \"Simplified\" License",
            "https://spdx.org/licenses/BSD-2-Clause.html",
        ),
    ],
    ids=[
        "Mozilla Public License 2.0",
        "GNU General Public License v2.0",
        "GNU General Public License v3.0",
        "GNU Lesser General Public License v2.1",
        "GNU Lesser General Public License v3.0",
        "The MIT License",
        "The 2-Clause BSD License",
    ],
)
def test_more_info_builtin_licenses(
    selenium, base_url, extension, license_name, license_link
):
    """Test all the builtin licenses offered by AMO by checking
    their names and links in the detail and version pages"""
    selenium.get(f"{base_url}/addon/{extension}/")
    # check the builtin license on the addon detail page
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert license_name in addon.more_info.addon_external_license_text
    addon.more_info.click_addon_external_license()
    addon.wait_for_current_url(license_link)
    selenium.get(f"{base_url}/addon/{extension}/versions/")
    # check the builtin license on the addon versions list page
    version = Versions(selenium, base_url).wait_for_page_to_load()
    assert license_name in version.versions_list[0].license_text
    version.versions_list[0].license_link.click()
    version.wait_for_current_url(license_link)


def test_more_info_reserved_license_is_not_linkified(selenium, base_url):
    """The 'All Rights Reserved' license is a simple text name and should be linkified"""
    selenium.get(f"{base_url}/addon/all-rights-reserved/")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert (
        "All Rights Reserved" in addon.more_info.addon_all_rights_reserved_license_text
    )
    # checks that there are no linked objects in more info license component
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, ".AddonMoreInfo-license a")
    selenium.get(f"{base_url}/addon/all-rights-reserved/versions/")
    version = Versions(selenium, base_url).wait_for_page_to_load()
    assert "All Rights Reserved" in version.versions_list[0].license_text
    # checks that there are no linked objects in version info license component
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, ".AddonVersionCard-license a")


@pytest.mark.nondestructive
def test_more_info_custom_license(selenium, base_url, variables):
    """Tests display of a custom license in 'More Info'."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon_name = addon.name
    # checks that the AMO custom license page opens and has the correct content
    custom_license = addon.more_info.click_addon_custom_license()
    assert (
        f"Custom License for {addon_name}"
        in custom_license.custom_licence_and_privacy_header
    )
    assert custom_license.custom_licence_and_privacy_text.is_displayed()
    assert custom_license.custom_licence_and_privacy_summary_card.is_displayed()


@pytest.mark.nondestructive
def test_more_info_privacy_policy(selenium, base_url, variables):
    """Tests presence and rendering of the add-on's privacy policy."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon_name = addon.name
    privacy = addon.more_info.click_addon_privacy_policy()
    # checks that the AMO privacy policy page opens and has the correct content
    assert (
        f"Privacy policy for {addon_name}" in privacy.custom_licence_and_privacy_header
    )
    assert privacy.custom_licence_and_privacy_text.is_displayed()
    assert privacy.custom_licence_and_privacy_summary_card.is_displayed()


@pytest.mark.nondestructive
def test_more_info_privacy_policy_missing(selenium, base_url, variables):
    """Tests behavior when privacy policy is missing."""
    extension = variables["addon_without_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    Detail(selenium, base_url).wait_for_page_to_load()
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CLASS_NAME, "AddonMoreInfo-privacy-policy-link")
    print("The add-on does not have a Privacy Policy")


@pytest.mark.nondestructive
def test_more_info_eula(selenium, base_url, variables):
    """Tests that the End-User License Agreement (EULA) is shown."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon_name = addon.name
    eula = addon.more_info.addon_eula()
    # checks that the AMO eula page opens and has the correct content
    assert (
        f"End-User License Agreement for {addon_name}"
        in eula.custom_licence_and_privacy_header
    )
    assert eula.custom_licence_and_privacy_text.is_displayed()
    assert eula.custom_licence_and_privacy_summary_card.is_displayed()


@pytest.mark.nondestructive
def test_more_info_eula_missing(selenium, base_url, variables):
    """Tests behavior when EULA is missing."""
    extension = variables["addon_without_stats"]
    selenium.get(f"{base_url}/addon/{extension}")
    Detail(selenium, base_url).wait_for_page_to_load()
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CLASS_NAME, "AddonMoreInfo-eula")
    print("The add-on does not have an End User License Agreement")


@pytest.mark.nondestructive
def test_compare_more_info_latest_version(selenium, base_url, variables):
    """Tests that the latest version info is used in the 'More Info' section."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon_name = addon.name
    more_info_version = addon.more_info.addon_version_number.text
    all_versions = addon.more_info.addon_versions()
    assert addon_name in all_versions.versions_page_header.text
    # verifies that the version number displayed in the more info card
    # matches the latest version number present in all versions page
    latest_version = all_versions.latest_version_number
    assert more_info_version == latest_version


@pytest.mark.nondestructive
def test_more_info_addon_tags(selenium, base_url, variables):
    """Tests that relevant tags are displayed in 'More Info'."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # get the name of one of the tags related to this addon
    tag_name = addon.more_info.addon_tags[0].text
    addon.more_info.addon_tags[0].click()
    # clicking on the tag opens a search results page with addons that share the same tag
    same_tag_results = Search(selenium, base_url).wait_for_page_to_load()
    # verifies that the results URL mention the tag name (encoded)
    assert f"/tag/{urllib.parse.quote(tag_name)}/" in selenium.current_url
    count = 0
    # checking that the first 5 search results do include the tag of the initial addon
    while count < 5:
        try:
            same_tag_results.result_list.click_search_result(count)
            # the 'click_search_result' function should already wait for the detail page to load
            # but I also want to check that the page switch occurred;
            # helps with debugging test failures
            addon.wait_for_current_url("firefox/addon/")
            tag_name_from_search = [el.text for el in addon.more_info.addon_tags]
            assert tag_name in tag_name_from_search, f"for {addon.name}"
            selenium.back()
            same_tag_results.search_results_list_loaded(5)
        except IndexError:
            print("There were less than 5 results matching the selected tag")
            break
        count += 1


@pytest.mark.nondestructive
@pytest.mark.skip(reason="need to update way of interaction")
def test_screenshot_viewer(selenium, base_url, variables):
    """Tests that the screenshot viewer works as expected."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert "Screenshots" in addon.screenshots.screenshot_section_header.text
    # clicks through each screenshot
    # and verifies that the screenshot full size viewer is opened
    # also check that the image preview sources
    # are actually retrieved from the server (no broken previews)
    for preview in addon.screenshots.screenshot_preview:
        preview_count = addon.screenshots.screenshot_preview.index(preview)
        preview.click()
        time.sleep(1)
        # check that he image preview is not broken
        src_img = selenium.find_elements(By.CSS_SELECTOR, ".ScreenShots-image")[
            preview_count
        ].get_attribute("src")
        assert requests.get(src_img, timeout=10).status_code == 200
        # checks that the screenshot viewer has opened
        addon.screenshots.screenshot_full_view_displayed()
        action = ActionChains(selenium)
        action.send_keys(Keys.ESCAPE)


@pytest.mark.nondestructive
def test_screenshot_ui_navigation(selenium, base_url, variables):
    """Tests UI navigation controls in the screenshot viewer."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.screenshots.screenshot_preview[0].click()
    time.sleep(1)
    # click on the right arrow to navigate to the next image
    # addon.screenshots.go_to_next_screenshot()
    action = ActionChains(selenium)
    action.send_keys(Keys.ARROW_RIGHT)
    assert "1 / 6" in addon.screenshots.screenshot_counter
    # click on the left arrow to navigate to the previous image
    action.send_keys(Keys.ARROW_LEFT)
    assert "1" in addon.screenshots.screenshot_counter


@pytest.mark.nondestructive
def test_screenshot_keyboard_navigation_tc_id_c4535(selenium, base_url, variables):
    """Tests keyboard navigation for screenshots."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    action = ActionChains(selenium)
    addon.screenshots.screenshot_preview[0].click()
    time.sleep(1)
    # send the right key to navigate to the next image
    action.send_keys(Keys.ARROW_RIGHT)
    assert "1 / 6" in addon.screenshots.screenshot_counter
    # send the left key to navigate to the previous image
    action.send_keys(Keys.ARROW_LEFT)
    assert "1" in addon.screenshots.screenshot_counter
    # send ESC to close the screenshot viewer
    action.send_keys(Keys.ESCAPE)


@pytest.mark.nondestructive
def test_add_to_collection_card(selenium, base_url, variables):
    """Tests the add-to-collection card on the add-on detail page."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # verifies that the Add to Collection card is present on the detail page
    assert "Add to collection" in addon.add_to_collection.collections_card_header
    assert addon.add_to_collection.collections_select_field.is_displayed()


# @pytest.mark.nondestructive
# def test_release_notes(selenium, base_url, variables):
#     """Tests the presence of release notes."""
#     extension = variables["detail_extension_slug"]
#     selenium.get(f"{base_url}/addon/{extension}")
#     addon = Detail(selenium, base_url).wait_for_page_to_load()
#     assert (
#         f"Release notes for {addon.more_info.addon_version_number.text}"
#         in addon.release_notes.release_notes_header
#     )
#     assert addon.release_notes.release_notes_text.is_displayed()


# @pytest.mark.nondestructive
# def test_more_addons_by_author_card(selenium, base_url, variables):
#     """Tests the display of other add-ons by the same author."""
#     extension = variables["experimental_addon"]
#     selenium.get(f"{base_url}/addon/{extension}")
#     addon = Detail(selenium, base_url).wait_for_page_to_load()
#     # verifies that the author name from the add-on summary card
#     # is also present in the add-ons by same author card
#     assert (
#         f"More extensions by {addon.authors.text}"
#         in addon.same_author_addons.addons_by_author_header
#     )
#     same_author_results = addon.same_author_addons.addons_by_author_results_list
#     # checks that up to six addons by the same author are displayed in the card
#     assert len(same_author_results) <= 6


# @pytest.mark.nondestructive
# def test_click_addon_in_more_addons_by_author(selenium, base_url, variables):
#     """Tests navigation when clicking an add-on in the author's section."""
#     extension = variables["experimental_addon"]
#     selenium.get(f"{base_url}/addon/{extension}")
#     addon = Detail(selenium, base_url).wait_for_page_to_load()
#     result_name = addon.same_author_addons.addons_by_author_results_items[0].text
#     # clicks on an addon present in the card and checks that the addon detail page is loaded
#     addon.same_author_addons.addons_by_author_results_items[0].click()
#     addon.wait_for_page_to_load()
#     assert result_name in addon.name


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_addon_description(selenium, base_url, variables):
    """Tests that the add-on description is displayed correctly."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert "About this extension" in addon.description.addon_description_header
    assert addon.description.addon_description_text.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_developer_comments(selenium, base_url, variables):
    """Tests display of developer comments on the add-on page."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon.description.read_more_button.is_displayed()
    addon.description.click_read_more_button()
    assert "Developer comments" in addon.developer_comments.header.text
    assert addon.developer_comments.content.is_displayed()


@pytest.mark.nondestructive
def test_addon_ratings_card(selenium, base_url, variables):
    """Tests display of the add-on's ratings card."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    assert "Rated" in addon.ratings.ratings_card_header
    # assert variables["ratings_card_summary"] in addon.ratings.ratings_card_summary
    # checks that the login button is present in the ratings card
    # when the add-on detail page is viewed by unauthenticated users
    assert addon.ratings.rating_login_button.is_displayed()
    # checks that all reviews link and report button are displayed
    assert addon.ratings.all_reviews_link.is_displayed()
    assert addon.ratings.report_abuse_button.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_addon_recommendations(selenium, base_url, variables):
    """Tests display of recommended add-ons."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    recommendations = addon.recommendations.addons_recommendations_results_list
    # verifies that the recommendations card shows up to 4 recommendations if available
    assert len(recommendations) <= 4


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_click_addon_recommendations(selenium, base_url, variables):
    """Tests clicking on a recommended add-on."""
    extension = variables["detail_extension_slug"]
    selenium.get(f"{base_url}/addon/{extension}")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    recommendation_name = addon.recommendations.recommendations_results_item[0].text
    # clicks on a recommendations and checks that the addon detail page is loaded
    addon.recommendations.recommendations_results_item[0].click()
    addon.wait_for_page_to_load()
    assert recommendation_name in addon.name

# More themes section not present in frontend anymore
# @pytest.mark.sanity
# @pytest.mark.nondestructive
# def test_theme_detail_page_tc_id_c95590(selenium, base_url, variables):
#     """Tests display and content of a theme's detail page."""
#     extension = variables["theme_detail_page"]
#     selenium.get(f"{base_url}/addon/{extension}")
#     addon = Detail(selenium, base_url).wait_for_page_to_load()
#     assert addon.themes.theme_preview.is_displayed()
#     # checks that we display More themes from the same artist and that
#     # each additional theme has its own preview from a total of 6
#     assert (
#         f"More themes by {addon.authors.text}"
#         in addon.same_author_addons.addons_by_author_header
#     )
#     theme_by_same_artist = addon.same_author_addons.addons_by_author_results_list
#     theme_by_same_artist_previews = addon.themes.more_themes_by_author_previews
#     assert len(theme_by_same_artist) <= 6
#     assert len(theme_by_same_artist) == len(theme_by_same_artist_previews)


# @pytest.mark.nondestructive
# def test_current_theme_not_in_more_by_artist_previews(selenium, base_url, variables):
#     """Tests that the current theme is not duplicated in the 'more by artist' section."""
#     extension = variables["theme_detail_page"]
#     selenium.get(f"{base_url}/addon/{extension}")
#     addon = Detail(selenium, base_url).wait_for_page_to_load()
#     # makes a record of the preview image source displayed first in the more themes by artist
#     # card, clicks on the preview and verifies that the theme is no longer present in
#     # the preview list since it is the currently opened theme detail page
#     theme_preview = addon.themes.more_themes_by_author_previews[0].get_attribute("src")
#     addon.themes.more_themes_by_author_previews[0].click()
#     addon.wait_for_page_to_load()
#     assert theme_preview not in addon.themes.preview_source

#  - to be removed, no url can be used in summary now
# def test_addon_summary_outgoing_urls(selenium, base_url):
#     """Checks that external URLs in summary are redirected through the outgoing domain"""
#     selenium.get(f"{base_url}/addon/outgoing-urls/")
#     Detail(selenium, base_url).wait_for_page_to_load()
#     addon_description
#     # outgoing_summary = addon.summary.find_element(By.CSS_SELECTOR, "p")
#     # assert (
#     #     "https://stage.outgoing.nonprod.webservices.mozgcp.net"
#     #     in addon.summary.text
#     # )
#     addon..click()
#     addon.wait_for_current_url("https://extensionworkshop.allizom.org/")


def test_addon_description_outgoing_urls(selenium, base_url):
    """Checks that external URLs in description are redirected through the outgoing domain"""
    selenium.get(f"{base_url}/addon/outgoing-urls/")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    outgoing_description = addon.description.addon_description_text.find_element(
        By.CSS_SELECTOR, "a"
    )
    assert (
        "https://stage.outgoing.nonprod.webservices.mozgcp.net"
        in outgoing_description.get_attribute("href")
    )
    outgoing_description.click()
    addon.wait_for_current_url("https://extensionworkshop.allizom.org/")


def test_addon_developer_comments_outgoing_urls(selenium, base_url):
    """Checks that external URLs in developer comments are redirected through the outgoing domain"""
    selenium.get(f"{base_url}/addon/outgoing-urls/")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    outgoing_dev_comments = addon.developer_comments.content.find_element(
        By.CSS_SELECTOR, "a"
    )
    assert (
        "https://stage.outgoing.nonprod.webservices.mozgcp.net"
        in outgoing_dev_comments.get_attribute("href")
    )
    outgoing_dev_comments.click()
    addon.wait_for_current_url("https://extensionworkshop.allizom.org/")


def test_addon_more_info_homepage_outgoing_urls(selenium, base_url):
    """Checks that external URLs in homepage are redirected through the outgoing domain"""
    selenium.get(f"{base_url}/addon/outgoing-urls/")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    outgoing_homepage = addon.more_info.addon_homepage_link
    assert (
        "https://stage.outgoing.nonprod.webservices.mozgcp.net"
        in outgoing_homepage.get_attribute("href")
    )
    outgoing_homepage.click()
    addon.wait_for_current_url("https://extensionworkshop.allizom.org/")


def test_addon_more_info_support_site_outgoing_urls(selenium, base_url):
    """Checks that external URLs in support site are redirected through the outgoing domain"""
    selenium.get(f"{base_url}/addon/outgoing-urls/")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    outgoing_support_site = addon.more_info.addon_support_site_link
    assert (
        "https://stage.outgoing.nonprod.webservices.mozgcp.net"
        in outgoing_support_site.get_attribute("href")
    )
    outgoing_support_site.click()
    addon.wait_for_current_url("https://extensionworkshop.allizom.org/")


def test_addon_custom_license_outgoing_urls(selenium, base_url):
    """Checks that external URLs in custom license are redirected through the outgoing domain"""
    selenium.get(f"{base_url}/addon/outgoing-urls/")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    custom_license = addon.more_info.click_addon_custom_license()
    outgoing_custom_license = (
        custom_license.custom_licence_and_privacy_text.find_element(
            By.CSS_SELECTOR, "a"
        )
    )
    assert (
        "https://stage.outgoing.nonprod.webservices.mozgcp.net"
        in outgoing_custom_license.get_attribute("href")
    )
    outgoing_custom_license.click()
    addon.wait_for_current_url("https://extensionworkshop.allizom.org/")


def test_addon_privacy_policy_outgoing_urls(selenium, base_url):
    """Checks that external URLs in privacy policy are redirected through the outgoing domain"""
    selenium.get(f"{base_url}/addon/outgoing-urls/")
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    privacy_policy = addon.more_info.click_addon_privacy_policy()
    outgoing_privacy_policy = (
        privacy_policy.custom_licence_and_privacy_text.find_element(
            By.CSS_SELECTOR, "a"
        )
    )
    assert (
        "https://stage.outgoing.nonprod.webservices.mozgcp.net"
        in outgoing_privacy_policy.get_attribute("href")
    )
    outgoing_privacy_policy.click()
    addon.wait_for_current_url("https://extensionworkshop.allizom.org/")

def test_addon_version_notes_outgoing_urls(selenium, base_url):
    """Checks that external URLs in release notes are redirected through the outgoing domain"""
    selenium.get(f"{base_url}/addon/outgoing-urls/")
    # check release notes in addon detail page
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    release_notes_outgoing = addon.release_notes.release_notes_text.find_element(
        By.CSS_SELECTOR, "a"
    )
    assert (
        "https://stage.outgoing.nonprod.webservices.mozgcp.net"
        in release_notes_outgoing.get_attribute("href")
    )
    release_notes_outgoing.click()
    addon.wait_for_current_url("https://extensionworkshop.allizom.org/")
    # check release notes in addon versions page
    selenium.get(f"{base_url}/addon/outgoing-urls/versions/")
    version = Versions(selenium, base_url).wait_for_page_to_load()
    version_notes_outgoing = version.versions_list[
        0
    ].version_release_notes.find_element(By.CSS_SELECTOR, "a")
    assert (
        "https://stage.outgoing.nonprod.webservices.mozgcp.net"
        in version_notes_outgoing.get_attribute("href")
    )
    version_notes_outgoing.click()
    addon.wait_for_current_url("https://extensionworkshop.allizom.org/")
