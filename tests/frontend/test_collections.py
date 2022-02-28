import pytest
import requests

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from pages.desktop.frontend.collections import Collections
from pages.desktop.frontend.details import Detail
from pages.desktop.frontend.search import Search
from scripts import reusables


@pytest.mark.serial
@pytest.mark.sanity
@pytest.mark.nondestructive
def test_collection_meta_card(selenium, base_url, variables):
    public_collection = variables['public_collection']
    selenium.get(f'{base_url}/collections{public_collection}')
    collection = Collections(selenium, base_url).wait_for_page_to_load()
    # checking that collection metadata elements are present in the summary card
    assert (
        variables['public_collection_name']
        in collection.collection_detail.collection_name
    )
    assert collection.collection_detail.collection_description.is_displayed()
    assert collection.collection_detail.collection_addons_number.is_displayed()
    assert collection.collection_detail.collection_creator.is_displayed()
    assert collection.collection_detail.collection_last_update_date.is_displayed()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_collection_addon_count_is_correct(selenium, base_url, variables):
    public_collection = variables['public_collection']
    selenium.get(f'{base_url}/collections{public_collection}')
    collection = Collections(selenium, base_url).wait_for_page_to_load()
    # checks that the addon count in the collection meta card matches
    # the actual number of addons present in the collection addons list
    assert int(collection.collection_detail.collection_stats[0].text) == len(
        collection.collection_detail.collection_addons_list
    )


@pytest.mark.serial
@pytest.mark.nondestructive
def test_collection_creator_and_modified_date(selenium, base_url, variables, wait):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.select_collection(0)
    # checks that the display name of the logged in user is present in the meta card
    assert 'collection_user' in collections.collection_detail.collection_stats[1].text
    # making a small edit to trigger a modified date change in the collection
    collections.collection_detail.click_edit_collection_button()
    collections.collection_detail.click_edit_collection_meta()
    collections.create.set_description(variables['collection_edit_description'])
    collections.create.save_collection()
    # waits for the list of collection stats to be loaded
    wait.until(lambda _: len(collections.collection_detail.collection_stats) == 3)
    # verifying that the collection modified date matches the actual current date
    wait.until(
        lambda _: collections.collection_detail.collection_stats[2].text
        == reusables.current_date(),
        message=f'Collections modified date "{collections.collection_detail.collection_stats[2].text}"'
        f'did not match actual date "{reusables.current_date()}"',
    )


@pytest.mark.serial
@pytest.mark.nondestructive
def test_my_collections_page_items(selenium, base_url, variables):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    # checking that various elements are present on the user collections page
    assert 'Collections' in collections.collections_summary_card_header
    assert variables['collections_card_summary'] in collections.collections_card_summary
    assert 'Create a collection' in collections.create_collection_button.text
    assert 'My collections' in collections.collections_list_header
    for collection in collections.list:
        assert collection.name.is_displayed()
        assert collection.number_of_addons.is_displayed()


@pytest.mark.serial
@pytest.mark.nondestructive
def test_select_collection_from_list(selenium, base_url, wait):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    # capture collection name and number of add-on displayed in My collections list
    list_collection_name = collections.list[0].name.text
    list_addon_count = collections.list[0].list_addons_count
    # selects collection from the list and verifies that the name of the collection
    # and the number of add-ons are matching those in the opened collection details
    collections.select_collection(0)
    assert list_collection_name == collections.collection_detail.collection_name
    wait.until(
        lambda _: list_addon_count
        == collections.collection_detail.collection_stats[0].text
    )


@pytest.mark.serial
@pytest.mark.nondestructive
def test_create_collection(selenium, base_url, variables, wait):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.click_create_collection()
    # using random strings to make sure we're always getting a unique URL,
    # which is constructed from the name of the collection
    name = reusables.get_random_string(15)
    collections.create.set_name(name)
    description = variables['collection_description']
    collections.create.set_description(description)
    collections.create.save_collection()
    collections.collection_detail.wait_for_details_to_load()
    # checks that the collection was created with the input given
    wait.until(
        lambda _: name == collections.collection_detail.collection_name,
        message=f'Expected collection name "{name}" was not displayed',
    )
    assert description == collections.collection_detail.collection_description.text


@pytest.mark.serial
@pytest.mark.nondestructive
def test_add_addons_to_collection(selenium, base_url, variables, wait):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.select_collection(0)
    collections.collection_detail.click_edit_collection_button()
    search_addon = collections.create.addon_search.search(variables['search_term'])
    # make a note of the first suggestion name
    suggestion_name = search_addon[0].name.text
    search_addon[0].name.click()
    # verify that a confirmation message is displayed when an addon is added to the collection
    assert 'Added to collection' in collections.create.addon_add_confirmation
    # waits for the addons list to be updated
    wait.until(
        lambda _: len(collections.create.edit_addons_list) > 0,
        message=f'Edit collection addon list had {len(collections.create.edit_addons_list)} addons',
    )
    # verifies that the suggestion selected was added to the collection
    assert (
        suggestion_name in collections.create.edit_addons_list[0].edit_list_addon_name
    )


@pytest.mark.serial
@pytest.mark.nondestructive
def test_collection_add_duplicate_addons_error(selenium, base_url, variables):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.select_collection(0)
    collections.collection_detail.click_edit_collection_button()
    # adds an add-on that already belongs to this collection and
    # verifies that the relevant error message is displayed
    search_addon = collections.create.addon_search.search(variables['search_term'])
    search_addon[0].name.click()
    assert (
        'This add-on already belongs to the collection'
        in collections.create.addon_add_failure
    )


@pytest.mark.serial
@pytest.mark.nondestructive
def test_remove_addon_from_collection(selenium, base_url, variables, wait):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.select_collection(0)
    collections.collection_detail.click_edit_collection_button()
    addons_list = len(collections.create.edit_addons_list)
    # adding a new addon to collection, then remove it
    search_addon = collections.create.addon_search.search(
        variables['detail_extension_name']
    )
    search_addon[0].name.click()
    # waits for the new addon to be added to the list
    wait.until(
        lambda _: len(collections.create.edit_addons_list) == addons_list + 1,
        message=f'Expected {addons_list + 1} addons but got {len(collections.create.edit_addons_list)} addons',
    )
    # make a note of the first add-on name in the list before removing it from the collection
    addon_name = collections.create.edit_addons_list[0].edit_list_addon_name
    collections.create.edit_addons_list[0].remove_addon()
    assert 'Removed from collection' in collections.create.removed_addon_confirmation
    # waits for the new addon to be removed from the list (list returns to initial state)
    wait.until(
        lambda _: len(collections.create.edit_addons_list) == addons_list,
        message=f'Expected {addons_list} addons but got {len(collections.create.edit_addons_list)} addons',
    )
    # checks that the addon we added at the beginning of the test was removed
    assert addon_name not in collections.create.edit_addons_list[0].edit_list_addon_name


@pytest.mark.skip(
    reason='There is an error preventing notes to be deleted. Skipping until the issue is fixed'
)
@pytest.mark.nondestructive
def test_collection_addon_notes(selenium, base_url, variables):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.select_collection(0)
    collections.collection_detail.click_edit_collection_button()
    # writing a note for an addon in the collection list
    collections.create.edit_addons_list[0].click_add_note()
    collections.create.edit_addons_list[0].note_input_text(
        variables['collection_addon_note']
    )
    collections.create.edit_addons_list[0].click_save_note()
    # check that the note written is displayed after saving
    assert (
        variables['collection_addon_note']
        in collections.create.edit_addons_list[0].note_text
    )
    # edit the collection addon note
    collections.create.edit_addons_list[0].click_edit_note()
    collections.create.edit_addons_list[0].note_input_text(
        variables['collection_addon_edited_note']
    )
    collections.create.edit_addons_list[0].click_save_note()
    # check that the edited note text is displayed after saving
    assert (
        variables['collection_addon_edited_note']
        in collections.create.edit_addons_list[0].note_text
    )
    collections.create.edit_addons_list[0].click_edit_note()
    # delete the collection note and check it is no longer displayed
    collections.create.edit_addons_list[0].click_delete_note()
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, '.EditableCollectionAddon-notes-content')


@pytest.mark.serial
@pytest.mark.nondestructive
def test_collection_sort_addons_by_date_added(selenium, base_url, variables, wait):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.select_collection(0)
    collections.collection_detail.click_edit_collection_button()
    # adding one more addon to the collection
    search_addon = collections.create.addon_search.search(
        variables['detail_extension_name']
    )
    search_addon[0].name.click()
    # waits for the new add-on to be added to the collection
    wait.until(
        lambda _: len(collections.create.edit_addons_list) == 2,
        message=f'The list contains {len(collections.create.edit_addons_list)} addons',
    )
    collections.collection_detail.click_back_to_collection()
    # using the Search class to interact with the list of addons present in the collection
    addons = Search(selenium, base_url).wait_for_page_to_load()
    sort = Select(collections.collection_detail.sort_addons)
    sort.select_by_visible_text('Oldest first')
    addons.wait_for_page_to_load()
    # this addon was already in the collection, so it is the older one when sort is applied
    assert variables['search_term'] in addons.result_list.extensions[0].name
    sort.select_by_visible_text('Newest first')
    addons.wait_for_page_to_load()
    # this is the new addon added to the collection, so it is the most recent when sort is applied
    assert variables['detail_extension_name'] in addons.result_list.extensions[0].name


@pytest.mark.serial
@pytest.mark.nondestructive
def test_collection_edit_metadata(selenium, base_url, variables, wait):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.select_collection(0)
    collections.collection_detail.click_edit_collection_button()
    # open the edit collection meta form
    collections.collection_detail.click_edit_collection_meta()
    # check that the save button is disabled if no changes are added yet
    assert collections.create.create_button_disabled.is_displayed()
    # click on cancel to close the edit collection meta form
    collections.collection_detail.cancel_edit_collection_meta()
    # open the edit collection meta form again
    collections.collection_detail.click_edit_collection_meta()
    # clear th current name and enter a new one
    collections.create.name_value.clear()
    collections.create.set_name(variables['collection_edit_name'])
    # edit the existing collection description
    collections.create.set_description(variables['collection_edit_description'])
    collections.create.save_collection()
    # verify that the updates are visible in their respective fields
    wait.until(
        lambda _: variables['collection_edit_name']
        in collections.collection_detail.collection_name
    )
    assert (
        variables['collection_edit_description']
        in collections.collection_detail.collection_description.text
    )


@pytest.mark.serial
@pytest.mark.nondestructive
def test_collection_addon_notes(selenium, base_url, variables):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.select_collection(0)
    collections.collection_detail.click_edit_collection_button()
    # writing a note for an addon in the collection list
    collections.create.edit_addons_list[0].click_add_note()
    collections.create.edit_addons_list[0].note_input_text(
        variables['collection_addon_note']
    )
    collections.create.edit_addons_list[0].click_save_note()
    # check that the note written is displayed after saving
    assert (
        variables['collection_addon_note']
        in collections.create.edit_addons_list[0].note_text
    )
    # edit the collection addon note
    collections.create.edit_addons_list[0].click_edit_note()
    collections.create.edit_addons_list[0].note_input_text(
        variables['collection_addon_edited_note']
    )
    collections.create.edit_addons_list[0].click_save_note()
    # check that the edited note text is displayed after saving
    assert (
        variables['collection_addon_edited_note']
        in collections.create.edit_addons_list[0].note_text
    )
    collections.create.edit_addons_list[0].click_edit_note()
    # delete the collection note and check it is no longer displayed
    collections.create.edit_addons_list[0].click_delete_note()
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, '.EditableCollectionAddon-notes-content')


@pytest.mark.serial
@pytest.mark.nondestructive
def test_add_to_collection_in_addon_detail_page(selenium, base_url, variables, wait):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    # make a note of the collection name to be used for this test
    collection_name = collections.list[0].name.text
    # make a note of the collections present in My Collections page
    my_collections_list = [el.name.text for el in collections.list]
    extension = variables['non_recommended_addon']
    # open an addon detail page
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    # make a note of the addon name to use it later
    addon_name = addon.name
    select = Select(addon.add_to_collection.collections_select_field)
    add_to_collection_list = [
        el.text for el in addon.add_to_collection.add_to_collections_list
    ]
    # check that the list of user collections matches the list present in Add to collection from detail page;
    # the detail page displays collections in alphabetical order, so we need to sort the other list to have a match
    assert sorted(my_collections_list, key=str.lower) == add_to_collection_list
    # add the addon to the test collection
    select.select_by_visible_text(collection_name)
    # verify that a success message is displayed once the collection is selected
    assert (
        f'Added to {collection_name}'
        in addon.add_to_collection.add_to_collection_success_notice
    )
    # select the same collection again and check that an error message is displayed
    select.select_by_visible_text(collection_name)
    assert (
        'This add-on already belongs to the collection'
        in addon.add_to_collection.add_to_collection_error_notice
    )
    collections.open().wait_for_page_to_load()
    # open the collection details and check that the new addon was included
    collections.select_collection(0)
    addons_list = Search(selenium, base_url).wait_for_page_to_load()
    assert addon_name in addons_list.result_list.extensions[0].name


@pytest.mark.serial
@pytest.mark.nondestructive
def test_delete_collection(selenium, base_url, variables):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    # make a note of the collection name in My Collections list
    collection_name = collections.list[0].name
    collections.select_collection(0)
    collections.collection_detail.delete_collection()
    # click on cancel to close the delete collection section
    collections.collection_detail.cancel_delete_collection()
    # open the delete section again and this time confirm
    collections.collection_detail.delete_collection()
    collections.collection_detail.confirm_delete_collection()
    # verify that the deleted collection is no longer present in My Collections
    assert collection_name not in [el.name for el in collections.list]


@pytest.mark.serial
@pytest.mark.nondestructive
def test_create_collection_from_addon_detail_page(selenium, base_url, variables, wait):
    extension = variables['non_recommended_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.login('collection_user')
    addon_name = addon.name
    select = Select(addon.add_to_collection.collections_select_field)
    # start the collection crete process from the addon detail page
    # which will automatically include the addon to the new collection
    select.select_by_visible_text('Create new collection')
    collections = Collections(selenium, base_url).wait_for_page_to_load()
    # fill up the collection creation form opened
    name = reusables.get_random_string(15)
    collections.create.set_name(name)
    collections.create.save_collection()
    # waits for the collection detail to be loaded after saving
    wait.until(lambda _: len(collections.create.edit_addons_list) > 0)
    collection_addon = collections.create.edit_addons_list[0].edit_list_addon_name
    # verify that the addon was indeed added to the collection
    assert addon_name == collection_addon
    # deleting the collection to avoid having too many collections for this test user
    collections.collection_detail.delete_collection()
    collections.collection_detail.confirm_delete_collection()


@pytest.mark.nondestructive
def test_collection_sort_addons_by_name(selenium, base_url, variables):
    public_collection = variables['public_collection']
    selenium.get(f'{base_url}/collections{public_collection}')
    collection = Collections(selenium, base_url).wait_for_page_to_load()
    # using the Search class to interact with the list of addons present in the collection
    addons = Search(selenium, base_url).wait_for_page_to_load()
    sort = Select(collection.collection_detail.sort_addons)
    sort.select_by_visible_text('Name')
    # waiting for the new addon sorting to take effect
    addons.wait_for_page_to_load()
    addons_list = [el.name for el in addons.result_list.extensions]
    # check that the addons list has been sorted alphabetically
    assert addons_list == sorted(addons_list)


@pytest.mark.nondestructive
def test_collection_sort_addons_by_popularity(selenium, base_url, variables):
    public_collection = variables['public_collection']
    selenium.get(f'{base_url}/collections{public_collection}')
    collection = Collections(selenium, base_url).wait_for_page_to_load()
    # using the Search class to interact with the list of addons present in the collection
    addons = Search(selenium, base_url).wait_for_page_to_load()
    sort = Select(collection.collection_detail.sort_addons)
    sort.select_by_visible_text('Popularity')
    # waiting for the new addon sorting to take effect
    addons.wait_for_page_to_load()
    # making a record of the list of addons after being sorted
    frontend_addons_list = [el.name for el in addons.result_list.extensions]
    # there is no way to directly determine that the sorting is correct in the frontend so we need to
    # take the api request sent by the frontend and compare the results with the api response
    request = requests.get(variables['public_collection_popularity'], timeout=10)
    response = request.json()
    # first, capture the popularity sorting, which is the 'weekly_downloads` property in the api response
    popularity = [result['addon']['weekly_downloads'] for result in response['results']]
    # first, check that the api is returning the addons sorted by weekly downloads in descending order
    assert popularity == sorted(popularity, reverse=True)
    # second, capture the list of addon names in the order they are returned by the api
    api_addon_name_list = [
        result['addon']['name']['en-US'] for result in response['results']
    ]
    # finally, make sure that the list of addons from the frontend matches the list of addons returned by the api
    assert api_addon_name_list == frontend_addons_list


@pytest.mark.nondestructive
def test_create_collection_empty_name(selenium, base_url):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.click_create_collection()
    assert collections.create.create_button_disabled.is_displayed()
    collections.create.set_slug('abc')
    assert collections.create.create_button_disabled.is_displayed()


@pytest.mark.nondestructive
def test_create_collection_with_only_symbols_name(selenium, base_url):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.click_create_collection()
    collections.create.set_name('<<!§')
    assert collections.create.create_button_disabled.is_displayed()


@pytest.mark.nondestructive
def test_create_collection_with_empty_custom_url(selenium, base_url):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.click_create_collection()
    collections.create.set_name('collection name')
    collections.create.slug_label_element.clear()
    assert collections.create.create_button_disabled.is_displayed()


@pytest.mark.nondestructive
def test_create_collection_with_already_used_url(selenium, base_url, variables):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.click_create_collection()
    collections.create.set_name('abc')
    collections.create.slug_label_element.clear()
    collections.create.set_slug('abc')
    collections.create.save_collection()
    collections.collection_detail.wait_for_details_to_load()
    # go back and try to create another collection with different name, but same URL
    collections.driver.get('https://addons.allizom.org/en-US/firefox/collections/')
    collections.click_create_collection()
    collections.create.set_name('def')
    collections.create.slug_label_element.clear()
    collections.create.set_slug('abc')
    collections.create.save_collection()
    assert variables['collection_reused_url_warning'] in collections.create.warning_text


@pytest.mark.nondestructive
def test_create_collection_with_invalid_symbols_in_url(selenium, base_url, variables):
    collections = Collections(selenium, base_url).open().wait_for_page_to_load()
    collections.login('collection_user')
    collections.click_create_collection()
    collections.create.set_name('abc')
    collections.create.set_slug('^_^')
    collections.create.save_collection()
    assert (
        variables['collection_invalid_custom_url_warning']
        in collections.create.warning_text
    )
