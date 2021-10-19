import pytest

from pages.desktop.collections import Collections
from scripts import reusables


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
