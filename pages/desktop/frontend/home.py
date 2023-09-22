import requests
from pypom import Region

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scripts import custom_waits
from pages.desktop.base import Base
from pages.desktop.frontend.details import Detail


class Home(Base):
    """Addons Home page"""

    _recommended_extensions_locator = (By.CLASS_NAME, "Home-Recommended-extensions")
    _recommended_themes_locator = (By.CLASS_NAME, "Home-Recommended-themes")
    _hero_locator = (By.CLASS_NAME, "HeroRecommendation")
    _secondary_hero_locator = (By.CLASS_NAME, "SecondaryHero")
    _popular_extensions_locator = (By.CLASS_NAME, "Home-PopularExtensions")
    _popular_themes_locator = (By.CLASS_NAME, "Home-Popular-themes")
    _themes_category_locator = (By.CLASS_NAME, "Home-CuratedThemes")
    _toprated_themes_locator = (By.CLASS_NAME, "Home-TopRatedThemes")
    _featured_collections_locator = (By.CLASS_NAME, "Home-FeaturedCollection")
    _shelves_titles_locator = (By.CSS_SELECTOR, ".CardList .Card-header-text")
    _shelves_see_more_links_locator = (
        By.CSS_SELECTOR,
        ".Card-shelf-footer-in-header a",
    )

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "LoadingText"))
        )
        return self

    @property
    def primary_hero(self):
        self.wait.until(EC.visibility_of_element_located(self._hero_locator))
        return self.find_element(*self._hero_locator)

    @property
    def hero_banner(self):
        self.wait.until(EC.visibility_of_element_located(self._hero_locator))
        el = self.find_element(*self._hero_locator)
        return self.PrimaryHero(self, el)

    @property
    def addon_shelf_titles(self):
        self.wait.until(EC.visibility_of_element_located(self._shelves_titles_locator))
        return [
            title.text for title in self.find_elements(*self._shelves_titles_locator)
        ]

    @property
    def popular_extensions(self):
        self.wait.until(
            EC.visibility_of_element_located(self._popular_extensions_locator)
        )
        el = self.find_element(*self._popular_extensions_locator)
        return self.Extensions(self, el)

    @property
    def recommended_extensions(self):
        self.wait.until(
            EC.visibility_of_element_located(self._recommended_extensions_locator)
        )
        el = self.find_element(*self._recommended_extensions_locator)
        return self.Extensions(self, el)

    @property
    def recommended_themes(self):
        self.wait.until(
            EC.visibility_of_element_located(self._recommended_themes_locator)
        )
        el = self.find_element(*self._recommended_themes_locator)
        return self.Themes(self, el)

    @property
    def popular_themes(self):
        self.wait.until(EC.visibility_of_element_located(self._popular_themes_locator))
        el = self.find_element(*self._popular_themes_locator)
        return self.Themes(self, el)

    @property
    def toprated_themes(self):
        self.wait.until(EC.visibility_of_element_located(self._toprated_themes_locator))
        el = self.find_element(*self._toprated_themes_locator)
        return self.Themes(self, el)

    @property
    def theme_category(self):
        self.wait.until(EC.visibility_of_element_located(self._themes_category_locator))
        el = self.find_element(*self._themes_category_locator)
        return self.ThemeCategory(self, el)

    @property
    def secondary_hero(self):
        self.wait.until(EC.visibility_of_element_located(self._secondary_hero_locator))
        el = self.find_element(*self._secondary_hero_locator)
        return self.SecondaryHero(self, el)

    @property
    def featured_collections(self):
        self.wait.until(
            EC.visibility_of_element_located(self._featured_collections_locator)
        )
        el = self.find_element(*self._featured_collections_locator)
        return self.Extensions(self, el)

    @property
    def see_more_links_in_shelves(self):
        self.wait.until(
            EC.visibility_of_element_located(self._shelves_see_more_links_locator)
        )
        return self.find_elements(*self._shelves_see_more_links_locator)

    def click_see_more_links(self, count):
        link = [el for el in self.see_more_links_in_shelves]
        target = link[count].get_attribute("target")
        # external links are opened in new tabs, so we need to account for multiple windows
        if target == "_blank":
            home_tab = self.driver.current_window_handle
            link[count].click()
            self.wait.until(EC.number_of_windows_to_be(2))
            new_tab = self.driver.window_handles[1]
            self.driver.switch_to.window(new_tab)
            # see more external links can contain variable content we might not know in advance (especially on prod)
            # the solution used here is to verify that the content we link to is available (i.e. page response = 200)
            self.wait.until(custom_waits.url_not_contains("about:blank"))
            page = requests.head(self.driver.current_url)
            assert (
                page.status_code == 200
            ), f"The response status code was {page.status_code}"
            self.driver.close()
            self.driver.switch_to.window(home_tab)
        else:
            # similar to external links, internal links might contain unpredictable content;
            # in this case, we check that the content exists inside the AMO domain
            link[count].click()
            self.wait.until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "LoadingText"))
            )
            assert "addons" in self.driver.current_url
            page = requests.head(self.driver.current_url)
            assert (
                page.status_code == 200
            ), f"The response status code was {page.status_code}"
            self.driver.back()
            # waits for the homepage to reload
            self.wait.until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "LoadingText"))
            )

    class ThemeCategory(Region):
        _home_theme_category_locator = (By.CLASS_NAME, "Home-SubjectShelf-list-item")
        _shelf_summary_locator = (By.CLASS_NAME, "Home-SubjectShelf-subheading")

        @property
        def list(self):
            self.wait.until(
                EC.visibility_of_element_located(self._home_theme_category_locator)
            )
            items = self.find_elements(*self._home_theme_category_locator)
            return [self.CategoryDetail(self.page, el) for el in items]

        @property
        def shelf_summary(self):
            self.wait.until(
                EC.visibility_of_element_located(self._shelf_summary_locator)
            )
            return self.find_element(*self._shelf_summary_locator).text

        class CategoryDetail(Region):
            _category_link_locator = (By.CLASS_NAME, "Home-SubjectShelf-link")
            _category_name_locator = (
                By.CSS_SELECTOR,
                ".Home-SubjectShelf-link span:nth-child(2)",
            )
            _category_icon_locator = (By.CLASS_NAME, "CategoryIcon")

            @property
            def name(self):
                self.wait.until(
                    EC.visibility_of_element_located(self._category_name_locator)
                )
                return self.find_element(*self._category_name_locator).text

            @property
            def category_icon(self):
                self.wait.until(
                    EC.visibility_of_element_located(self._category_icon_locator)
                )
                return self.find_element(*self._category_icon_locator)

            def click(self):
                self.root.click()
                from pages.desktop.frontend.search import Search

                return Search(self.driver, self.page.base_url)

    class Extensions(Region):
        _browse_all_locator = (By.CSS_SELECTOR, ".Card-shelf-footer-in-header a")
        _extensions_locator = (By.CLASS_NAME, "SearchResult")
        _promo_card_header_locator = (By.CLASS_NAME, "Card-header-text")

        @property
        def list(self):
            self.wait.until(EC.visibility_of_element_located(self._extensions_locator))
            items = self.find_elements(*self._extensions_locator)
            return [Home.PromoShelvesAddons(self.page, el) for el in items]

        def browse_all(self):
            self.wait.until(EC.visibility_of_element_located(self._browse_all_locator))
            self.find_element(*self._browse_all_locator).click()
            from pages.desktop.frontend.search import Search

            search = Search(self.driver, self.page.base_url)
            return search.wait_for_page_to_load()

        @property
        def card_header(self):
            self.wait.until(
                EC.visibility_of_element_located(self._promo_card_header_locator)
            )
            return self.find_element(*self._promo_card_header_locator).text

        def see_collection_details(self):
            self.wait.until(EC.visibility_of_element_located(self._browse_all_locator))
            self.find_element(*self._browse_all_locator).click()
            # TODO: add additional validations when I'm covering collections

    class Themes(Region):
        _browse_all_locator = (By.CSS_SELECTOR, ".Card-shelf-footer-in-header a")
        _themes_locator = (By.CLASS_NAME, "SearchResult--theme")
        _promo_card_header_locator = (By.CLASS_NAME, "Card-header-text")

        @property
        def list(self):
            self.wait.until(EC.visibility_of_element_located(self._themes_locator))
            items = self.find_elements(*self._themes_locator)
            return [Home.PromoShelvesAddons(self.page, el) for el in items]

        def browse_all(self):
            self.wait.until(EC.visibility_of_element_located(self._browse_all_locator))
            self.find_element(*self._browse_all_locator).click()
            from pages.desktop.frontend.search import Search

            search = Search(self.driver, self.page.base_url)
            return search.wait_for_page_to_load()

        @property
        def card_header(self):
            self.wait.until(
                EC.visibility_of_element_located(self._promo_card_header_locator)
            )
            return self.find_element(*self._promo_card_header_locator).text

    class PromoShelvesAddons(Region):
        _addon_link_locator = (By.CLASS_NAME, "SearchResult-link")
        _addon_name_locator = (By.CLASS_NAME, "SearchResult-name")
        _addon_icon_locator = (By.CLASS_NAME, "SearchResult-icon")
        _addon_users_locator = (By.CLASS_NAME, "SearchResult-users-text")
        _addon_rating_locator = (By.CLASS_NAME, "SearchResult-rating")

        @property
        def name(self):
            self.wait.until(EC.visibility_of_element_located(self._addon_name_locator))
            return self.find_element(*self._addon_name_locator)

        def click(self):
            self.wait.until(EC.element_to_be_clickable(self._addon_link_locator))
            self.find_element(*self._addon_link_locator).click()
            from pages.desktop.frontend.extensions import Extensions

            return Extensions(self.driver, self.page.base_url)

        @property
        def addon_icon_preview(self):
            self.wait.until(EC.visibility_of_element_located(self._addon_icon_locator))
            return self.find_element(*self._addon_icon_locator)

        @property
        def addon_users_preview(self):
            self.wait.until(EC.visibility_of_element_located(self._addon_users_locator))
            return self.find_element(*self._addon_users_locator)

        @property
        def addon_rating_preview(self):
            self.wait.until(
                EC.visibility_of_element_located(self._addon_rating_locator)
            )
            return self.find_element(*self._addon_rating_locator)

        def shelf_item_elements(self, item):
            assert item.name
            assert item.addon_icon_preview.is_displayed()
            assert item.addon_users_preview.is_displayed()

    class PrimaryHero(Region):
        _hero_locator = (By.CLASS_NAME, "HeroRecommendation")
        _hero_image_locator = (By.CLASS_NAME, "HeroRecommendation-image")
        _hero_title_locator = (By.CLASS_NAME, "HeroRecommendation-title-text")
        _hero_extension_name_locator = (By.CLASS_NAME, "HeroRecommendation-heading")
        _hero_extension_summary_locator = (By.CLASS_NAME, "HeroRecommendation-body")
        _extension_button_locator = (By.CLASS_NAME, "HeroRecommendation-link")
        _extension_link_locator = (By.CSS_SELECTOR, ".HeroRecommendation-info a")

        @property
        def primary_hero_banner(self):
            self.wait.until(EC.visibility_of_element_located(self._hero_locator))
            return self.find_element(*self._hero_locator)

        @property
        def primary_hero_image(self):
            self.wait.until(EC.visibility_of_element_located(self._hero_image_locator))
            return self.find_element(*self._hero_image_locator)

        @property
        def primary_hero_title(self):
            self.wait.until(EC.visibility_of_element_located(self._hero_title_locator))
            return self.find_element(*self._hero_title_locator).text

        @property
        def primary_hero_extension_name(self):
            self.wait.until(
                EC.visibility_of_element_located(self._hero_extension_name_locator)
            )
            return self.find_element(*self._hero_extension_name_locator).text

        @property
        def primary_hero_extension_summary(self):
            self.wait.until(
                EC.visibility_of_element_located(self._hero_extension_summary_locator)
            )
            return self.find_element(*self._hero_extension_summary_locator)

        def click_hero_extension_link(self):
            self.wait.until(EC.element_to_be_clickable(self._extension_button_locator))
            self.find_element(*self._extension_button_locator).click()
            return Detail(self.driver, self.page.base_url).wait_for_page_to_load()

    class SecondaryHero(Region):
        _secondary_headline_locator = (By.CLASS_NAME, "SecondaryHero-message-headline")
        _secondary_description_locator = (
            By.CLASS_NAME,
            "SecondaryHero-message-description",
        )
        _see_all_extensions_locator = (By.CLASS_NAME, "SecondaryHero-message-link")
        _modules_locator = (By.CLASS_NAME, "SecondaryHero-module")

        @property
        def secondary_hero_headline(self):
            self.wait.until(
                EC.visibility_of_element_located(self._secondary_headline_locator)
            )
            return self.find_element(*self._secondary_headline_locator).text

        @property
        def secondary_hero_description(self):
            self.wait.until(
                EC.visibility_of_element_located(self._secondary_description_locator)
            )
            return self.find_element(*self._secondary_description_locator).text

        def see_all_extensions(self):
            self.wait.until(
                EC.element_to_be_clickable(self._see_all_extensions_locator)
            )
            self.find_element(*self._see_all_extensions_locator).click()
            from pages.desktop.frontend.extensions import Extensions

            return Extensions(self.driver, self.page.base_url).wait_for_page_to_load()

        @property
        def secondary_hero_modules(self):
            self.wait.until(EC.visibility_of_element_located(self._modules_locator))
            element = self.find_elements(*self._modules_locator)
            return [self.SecondaryHeroModules(self.page, el) for el in element]

        class SecondaryHeroModules(Region):
            _module_icon_locator = (By.CLASS_NAME, "SecondaryHero-module-icon")
            _module_description_locator = (
                By.CLASS_NAME,
                "SecondaryHero-module-description",
            )
            _module_link_locator = (By.CSS_SELECTOR, ".SecondaryHero-module a")
            _module_link_text_locator = (By.CLASS_NAME, "SecondaryHero-module-linkText")

            @property
            def module_icon(self):
                self.wait.until(
                    EC.visibility_of_element_located(self._module_icon_locator)
                )
                return self.find_element(*self._module_icon_locator)

            @property
            def module_description(self):
                self.wait.until(
                    EC.visibility_of_element_located(self._module_description_locator)
                )
                return self.find_element(*self._module_description_locator)

            def click_secondary_module_link(self):
                link = self.find_element(*self._module_link_locator)
                target = link.get_attribute("target")
                # external links are opened in new tabs, so we need to account for multiple windows
                if target == "_blank":
                    link.click()
                    self.wait.until(EC.number_of_windows_to_be(2))
                    new_tab = self.driver.window_handles[1]
                    self.driver.switch_to.window(new_tab)
                    # editorial might change these links when they need to push new content and we don't know
                    # in advance what that content might be; also, we want to avoid frequent maintenance for
                    # these tests; the solution used is to verify that the content we link to is available
                    # (i.e. we check that the page response status is 200)
                    self.wait.until(custom_waits.url_not_contains("about:blank"))
                    page = requests.head(self.driver.current_url)
                    assert (
                        page.status_code == 200
                    ), f"The response status code was {page.status_code}"
                else:
                    # this condition handles links that open on the amo domain; again, we might not know the
                    # content in advance, so the best we can do is check that the page opens in AMO
                    # and the status code we receive is 200
                    link.click()
                    self.wait.until(
                        EC.invisibility_of_element_located(
                            (By.CLASS_NAME, "LoadingText")
                        )
                    )
                    assert "addons" in self.driver.current_url
                    page = requests.head(self.driver.current_url)
                    assert (
                        page.status_code == 200
                    ), f"The response status code was {page.status_code}"
