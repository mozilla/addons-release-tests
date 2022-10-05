import pytest
from pypom import Region

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.desktop.base import Base


class Collections(Base):
    URL_TEMPLATE = 'collections/'

    _collections_card_header_locator = (By.CSS_SELECTOR, '.CollectionList-info header')
    _collections_card_summary_locator = (By.CLASS_NAME, 'CollectionList-info-text')
    _collections_create_button_locator = (By.CLASS_NAME, 'CollectionList-create')
    _my_collections_list_header_locator = (
        By.CSS_SELECTOR,
        '.CollectionList-list header',
    )
    _collection_item_locator = (By.CLASS_NAME, 'UserCollection')

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText')),
            message='The collections page was not loaded',
        )
        return self

    @property
    def list(self):
        """Represents the list of collections form My Collections page"""
        items = self.find_elements(*self._collection_item_locator)
        return [self.Collection(self, el) for el in items]

    @property
    def collections_list_header(self):
        return self.find_element(*self._my_collections_list_header_locator).text

    @property
    def collections_summary_card_header(self):
        return self.find_element(*self._collections_card_header_locator).text

    @property
    def collections_card_summary(self):
        return self.find_element(*self._collections_card_summary_locator).text

    def select_collection(self, count):
        # wait needed to avoid a weird bug on the site where you land on the
        # homepage when clicking on a collection before the name is visible
        self.wait.until(lambda _: len(self.list[0].name.text) > 0)
        self.find_elements(*self._collection_item_locator)[count].click()
        return self.CollectionDetail(self).wait_for_details_to_load()

    @property
    def collection_detail(self):
        return self.CollectionDetail(self)

    @property
    def create_collection_button(self):
        return self.find_element(*self._collections_create_button_locator)

    def click_create_collection(self):
        self.find_element(*self._collections_create_button_locator).click()
        self.wait.until(
            lambda _: self.is_element_displayed(
                By.CSS_SELECTOR, '.CollectionManager-submit.Button--disabled'
            ),
            message='The collection save button was not displayed. The collection create form was not loaded properly',
        )

    @property
    def create(self):
        return self.CollectionCreate(self)

    class Collection(Region):
        """Represents an individual collection in My collections list."""

        _name_locator = (By.CLASS_NAME, 'UserCollection-name')
        _link_locator = (By.CLASS_NAME, 'UserCollection-link')
        _addon_number_locator = (By.CLASS_NAME, 'UserCollection-number')

        @property
        def name(self):
            return self.find_element(*self._name_locator)

        @property
        def link(self):
            return self.find_element(*self._link_locator)

        @property
        def number_of_addons(self):
            return self.find_element(*self._addon_number_locator)

        @property
        def list_addons_count(self):
            count = self.number_of_addons.text
            return count.split()[0].replace(' add-ons', '')

    class CollectionCreate(Region):
        """Represents the collections create form."""

        _name_input_locator = (By.ID, 'collectionName')
        _description_input_locator = (By.ID, 'collectionDescription')
        _slug_input_locator = (By.ID, 'collectionSlug')
        _cancel_button_locator = (By.CLASS_NAME, 'CollectionManager-cancel')
        _create_button_disabled_locator = (
            By.CSS_SELECTOR,
            '.CollectionManager-submit.Button--disabled',
        )
        _create_button_locator = (By.CSS_SELECTOR, '.CollectionManager-submit')
        _placeholder_locator = (By.CLASS_NAME, 'Collection-placeholder')
        _add_success_message_locator = (By.CSS_SELECTOR, '.Notice-success p')
        _add_error_message_locator = (By.CSS_SELECTOR, '.Notice-error p')
        _removed_addon_notice_locator = (By.CSS_SELECTOR, '.Notice-generic p')
        _edit_collection_addons_list_locator = (
            By.CSS_SELECTOR,
            '.EditableCollectionAddon',
        )

        _warning_text_locator = (By.CSS_SELECTOR, '.Notice-error .Notice-text')

        def set_name(self, value):
            self.find_element(*self._name_input_locator).send_keys(value)

        @property
        def name_value(self):
            return self.find_element(*self._name_input_locator)

        def set_description(self, value):
            self.find_element(*self._description_input_locator).send_keys(value)

        @property
        def description_value(self):
            return self.find_element(*self._description_input_locator).text

        def set_slug(self, value):
            self.find_element(*self._slug_input_locator).send_keys(value)

        @property
        def slug_value(self):
            return self.find_element(*self._description_input_locator).text

        @property
        def slug_label_element(self):
            return self.find_element(*self._slug_input_locator)

        @property
        def cancel_creation(self):
            return self.find_element(*self._cancel_button_locator)

        @property
        def create_button_disabled(self):
            return self.find_element(*self._create_button_disabled_locator)

        def save_collection(self):
            self.find_element(*self._create_button_locator).click()
            return (
                Collections(self.driver, self.page)
                .CollectionDetail(self)
                .wait_for_details_to_load()
            )

        @property
        def warning_text(self):
            self.wait.until(
                EC.visibility_of_element_located(self._warning_text_locator)
            )
            return self.find_element(*self._warning_text_locator).text

        @property
        def addon_search(self):
            return self.AddonSearch(self)

        class AddonSearch(Region):
            _header_locator = (By.CSS_SELECTOR, '.AutoSearchInput-label')
            _root_locator = (By.CSS_SELECTOR, '.CollectionAddAddon')
            _search_field_locator = (By.ID, 'AutoSearchInput-collection-addon-query')
            _search_list_locator = (
                By.CSS_SELECTOR,
                '.AutoSearchInput-suggestions-list',
            )
            _search_item_locator = (
                By.CSS_SELECTOR,
                '.AutoSearchInput-suggestions-item',
            )

            @property
            def header(self):
                return self.find_element(*self._header_locator)

            def search(self, term):
                textbox = self.find_element(*self._search_field_locator)
                textbox.click()
                textbox.send_keys(term)
                return self.search_items()

            def search_items(self):
                self.wait.until(
                    lambda _: self.is_element_displayed(*self._search_list_locator),
                    message='Search suggestions list was not loaded',
                )
                WebDriverWait(self.driver, 30).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText')),
                    message='There were no search suggestions loaded for the used query',
                )
                search_list = self.find_element(*self._search_list_locator)
                items = search_list.find_elements(*self._search_item_locator)
                return [self.SearchItems(self, el) for el in items]

            class SearchItems(Region):
                _item_name_locator = (By.CSS_SELECTOR, '.SearchSuggestion-name')

                @property
                def name(self):
                    return self.find_element(*self._item_name_locator)

        @property
        def addon_add_confirmation(self):
            self.wait.until(
                EC.visibility_of_element_located(self._add_success_message_locator),
                message='There was no success message displayed after the addon was added to the collection',
            )
            return self.find_element(*self._add_success_message_locator).text

        @property
        def addon_add_failure(self):
            self.wait.until(
                EC.visibility_of_element_located(self._add_error_message_locator),
                message='There was no error message displayed when the addon failed to be added to the collection',
            )
            return self.find_element(*self._add_error_message_locator).text

        @property
        def removed_addon_confirmation(self):
            self.wait.until(
                EC.visibility_of_element_located(self._removed_addon_notice_locator),
                message='There was no success message displayed after the addon was removed from the collection',
            )
            return self.find_element(*self._removed_addon_notice_locator).text

        @property
        def edit_addons_list(self):
            items = self.find_elements(*self._edit_collection_addons_list_locator)
            return [self.EditAddonsList(self, el) for el in items]

        class EditAddonsList(Region):
            _edit_list_addon_name_locator = (
                By.CLASS_NAME,
                'EditableCollectionAddon-name',
            )
            _add_note_button_locator = (
                By.CLASS_NAME,
                'EditableCollectionAddon-leaveNote-button',
            )
            _add_note_textarea_locator = (By.CLASS_NAME, 'DismissibleTextForm-textarea')
            _save_note_button_locator = (By.CLASS_NAME, 'DismissibleTextForm-submit')
            _note_text_locator = (
                By.CLASS_NAME,
                'EditableCollectionAddon-notes-content',
            )
            _edit_addon_note_button_locator = (
                By.CLASS_NAME,
                'EditableCollectionAddon-notes-edit-button',
            )
            _delete_addon_note_button_locator = (
                By.CLASS_NAME,
                'DismissibleTextForm-delete',
            )
            _remove_addon_button_locator = (
                By.CLASS_NAME,
                'EditableCollectionAddon-remove-button',
            )

            @property
            def edit_list_addon_name(self):
                return self.find_element(*self._edit_list_addon_name_locator).text

            def click_add_note(self):
                self.find_element(*self._add_note_button_locator).click()
                self.wait.until(
                    EC.visibility_of_element_located(self._add_note_textarea_locator),
                    message='Collection addon note text input area was not displayed',
                )

            def note_input_text(self, value):
                self.find_element(*self._add_note_textarea_locator).send_keys(value)

            def clear_collection_note_text_field(self):
                self.find_element(*self._add_note_textarea_locator).clear()

            @property
            def note_input_value(self):
                return self.find_element(*self._add_note_textarea_locator).text

            def click_save_note(self):
                self.find_element(*self._save_note_button_locator).click()
                self.wait.until(
                    EC.visibility_of_element_located(self._note_text_locator),
                    message='The collection addon note was not visible after saving',
                )

            @property
            def note_text(self):
                return self.find_element(*self._note_text_locator).text

            def click_edit_note(self):
                self.find_element(*self._edit_addon_note_button_locator).click()
                self.wait.until(
                    EC.visibility_of_element_located(self._add_note_textarea_locator),
                    message='Collection addon note text input area was not displayed',
                )

            def click_delete_note(self):
                self.find_element(*self._delete_addon_note_button_locator).click()
                # waiting for the comment textarea to be closed after the note is deleted
                try:
                    self.wait.until(
                        EC.invisibility_of_element_located(
                            self._add_note_textarea_locator
                        ),
                        message='The collection note could not be deleted',
                    )
                # if the note could not be deleted because of a field error,
                # we need to catch that error and force the test to fail
                except TimeoutException:
                    error = self.driver.find_element(
                        By.CSS_SELECTOR, '.ErrorList p'
                    ).text
                    pytest.fail(error)

            def remove_addon(self):
                self.find_element(*self._remove_addon_button_locator).click()
                self.wait.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, '.Notice-generic')
                    ),
                    message='Success message was not displayed after the addon has been removed from the collection',
                )

    class CollectionDetail(Region):
        """Represents the detail page of a collection."""

        _name_locator = (By.CLASS_NAME, 'CollectionDetails-title')
        _summary_locator = (By.CLASS_NAME, 'CollectionDetails-description')
        _addon_count_locator = (By.CSS_SELECTOR, '.MetadataCard dl:nth-child(1)')
        _collection_creator_locator = (By.CSS_SELECTOR, '.MetadataCard dl:nth-child(2)')
        _last_modified_date_locator = (By.CSS_SELECTOR, '.MetadataCard dl:nth-child(3)')
        _stats_data_locator = (By.CSS_SELECTOR, '.MetadataCard dd')
        _collection_addons_list_locator = (By.CSS_SELECTOR, '.SearchResult-result')
        _edit_button_locator = (By.CLASS_NAME, 'CollectionDetails-edit-button')
        _edit_details_button_locator = (
            By.CLASS_NAME,
            'CollectionDetails-edit-details-button',
        )
        _cancel_collection_edit_locator = (
            By.CLASS_NAME,
            'CollectionDetails-back-to-collection-button',
        )
        _cancel_meta_edit_button_locator = (
            By.CSS_SELECTOR,
            '.CollectionManager-cancel',
        )
        _delete_button_locator = (By.CLASS_NAME, 'Collection-delete-button')
        _confirm_delete_dialog_locator = (
            By.CSS_SELECTOR,
            '.ConfirmationDialog-message',
        )
        _cancel_delete_button_locator = (
            By.CSS_SELECTOR,
            '.ConfirmationDialog-cancel-button',
        )
        _confirm_delete_button_locator = (
            By.CSS_SELECTOR,
            '.ConfirmationDialog-confirm-button',
        )
        _collection_addons_sort_locator = (By.ID, 'CollectionSort-select')

        def wait_for_details_to_load(self):
            """Waits for various page components to be loaded"""
            self.wait.until(
                EC.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText')),
                message='The collections detail page was not loaded',
            )
            return self

        @property
        def collection_name(self):
            return self.find_element(*self._name_locator).text

        @property
        def collection_description(self):
            return self.find_element(*self._summary_locator)

        @property
        def collection_addons_number(self):
            return self.find_element(*self._addon_count_locator)

        @property
        def collection_creator(self):
            return self.find_element(*self._collection_creator_locator)

        @property
        def collection_last_update_date(self):
            return self.find_element(*self._last_modified_date_locator)

        @property
        def collection_stats(self):
            return self.find_elements(*self._stats_data_locator)

        @property
        def collection_addons_list(self):
            return self.find_elements(*self._collection_addons_list_locator)

        def click_edit_collection_button(self):
            self.find_element(*self._edit_button_locator).click()
            self.wait.until(
                lambda _: self.is_element_displayed(
                    By.ID, 'AutoSearchInput-collection-addon-query'
                ),
                message='The edit collection search component was not loaded',
            )

        def click_back_to_collection(self):
            self.find_element(*self._cancel_collection_edit_locator).click()
            self.wait.until(
                EC.element_to_be_clickable(self._edit_button_locator),
                message='Could not interact with the "Back to collection" button',
            )

        def click_edit_collection_meta(self):
            self.find_element(*self._edit_details_button_locator).click()
            self.wait.until(
                EC.visibility_of_element_located(self._cancel_meta_edit_button_locator),
                message='The edit collection meta form was not displayed',
            )

        def cancel_edit_collection_meta(self):
            self.find_element(*self._cancel_meta_edit_button_locator).click()
            self.wait.until(
                EC.element_to_be_clickable(self._edit_details_button_locator),
                message='The edit collection meta form could not be closed',
            )

        def delete_collection(self):
            self.find_element(*self._delete_button_locator).click()
            self.wait.until(
                EC.element_to_be_clickable(self._confirm_delete_button_locator),
                message='The delete collection confirmation section was not displayed',
            )

        @property
        def confirm_delete_dialog_message(self):
            return self.find_element(*self._confirm_delete_dialog_locator)

        @property
        def cancel_delete_collection_button(self):
            return self.find_element(*self._cancel_delete_button_locator)

        def cancel_delete_collection(self):
            self.find_element(*self._cancel_delete_button_locator).click()
            self.wait.until(
                EC.element_to_be_clickable(self._delete_button_locator),
                message='The delete collection confirmation section could not be closed',
            )

        @property
        def confirm_delete_collection_button(self):
            return self.find_element(*self._confirm_delete_button_locator)

        def confirm_delete_collection(self):
            self.find_element(*self._confirm_delete_button_locator).click()
            return Collections(self.driver, self.page).wait_for_page_to_load()

        @property
        def sort_addons(self):
            return self.find_element(*self._collection_addons_sort_locator)
