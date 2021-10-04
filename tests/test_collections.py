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
    collections.login('regular_user')
    collections.select_collection(0)
    # checks that the display name of the logged in user is present in the meta card
    assert 'regular_user' in collections.collection_detail.collection_stats[1].text
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
    collections.login('regular_user')
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
    collections.login('regular_user')
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
