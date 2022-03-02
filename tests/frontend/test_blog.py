import pytest

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.frontend.blog import BlogHomepage, ArticlePage
from pages.desktop.frontend.home import Home


@pytest.mark.sanity
@pytest.mark.nondesstructive
def test_blog_homepage_header_logo_button(base_url, selenium):
    page = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    page.header.click_title()
    homepage = Home(selenium, base_url)
    assert homepage.primary_hero.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondesstructive
def test_articles_elements_are_displayed(base_url, selenium):
    page = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    for article in page.articles:
        assert article.image.is_displayed()
        assert article.title.is_displayed()
        assert article.date.is_displayed()
        assert article.intro_text.is_displayed()
        assert article.read_more_link.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondesstructive
def test_open_article_by_clicking_article_image(base_url, selenium):
    page = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    article_title = page.articles[0].title.text
    page.articles[0].image.click()
    article_page = ArticlePage(selenium, base_url)
    assert article_title.lower() in article_page.title.text.lower()


@pytest.mark.sanity
@pytest.mark.nondesstructive
def test_open_article_by_clicking_article_title(base_url, selenium):
    page = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    article_title = page.articles[0].title.text
    page.articles[0].title.click()
    article_page = ArticlePage(selenium, base_url)
    assert article_title.lower() in article_page.title.text.lower()


@pytest.mark.nondesstructive
def test_open_article_by_clicking_read_more_link(base_url, selenium):
    page = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    article_title = page.articles[0].title.text
    page.articles[0].read_more_link.click()
    article_page = ArticlePage(selenium, base_url)
    assert article_title.lower() in article_page.title.text.lower()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_article_page_loaded_correctly(base_url, selenium, variables):
    blog_homepage = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    page = blog_homepage.articles[0].click_read_more_link()
    assert page.header_logo.is_displayed()
    assert page.title.is_displayed()
    assert page.author.name.is_displayed()
    assert page.author.picture.is_displayed()
    assert page.author.twitter_link.is_displayed()
    assert page.author.pocket_link.is_displayed()
    for link in page.nav_bar_links:
        assert link.is_displayed()
    # verify that the article has at least one paragraph
    assert page.content_paragraphs[0].is_displayed()
    # verify that at least one of next/prev article links is displayed
    try:
        assert page.next_article.is_displayed()
    except NoSuchElementException:
        page.previous_article.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_article_page_header_logo_button(base_url, selenium, variables):
    blog_homepage = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    page = blog_homepage.articles[0].click_read_more_link()
    page.header_logo.click()
    homepage = Home(selenium, base_url)
    assert homepage.primary_hero.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_navbar_frontend_homepage_link(base_url, selenium, variables):
    blog_homepage = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    page = blog_homepage.articles[0].click_read_more_link()
    page.nav_bar_links[0].click()
    homepage = Home(selenium, base_url)
    assert homepage.primary_hero.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_navbar_blog_homepage_link(base_url, selenium, variables):
    blog_homepage = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    page = blog_homepage.articles[0].click_read_more_link()
    page.nav_bar_links[1].click()
    blog_homepage = BlogHomepage(selenium, base_url)
    assert blog_homepage.articles[0].title.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_navbar_current_article_link(base_url, selenium, variables):
    blog_homepage = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    page = blog_homepage.articles[0].click_read_more_link()
    initial_title = page.title.text
    page.nav_bar_links[2].click()
    assert initial_title in page.title.text


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_next_and_previous_article_links(base_url, selenium, variables):
    blog_homepage = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    page = blog_homepage.articles[0].click_read_more_link()
    initial_title = page.title.text
    page.next_article.click()
    assert initial_title not in page.title.text
    page.previous_article.click()
    assert initial_title in page.title.text


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_addon_cards_loaded_correctly(base_url, selenium, variables):
    blog_homepage = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    page = blog_homepage.articles[0].click_read_more_link()
    for card in page.addon_cards:
        assert card.title.is_displayed()
        assert card.author.is_displayed()
        assert len(card.summary) > 0
        assert 0 <= card.rating <= 5
        assert card.users_number >= 0
        assert card.add_to_firefox_button.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_addon_card_recommendation_badge_link(base_url, selenium, variables):
    blog_homepage = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    page = blog_homepage.articles[0].click_read_more_link()
    for addon_card in page.addon_cards:
        if addon_card.is_recommended:
            addon_card.recommended_link.click()
            initial_window = page.driver.window_handles[0]
            child_window = page.driver.window_handles[1]
            page.driver.switch_to.window(child_window)
            page.wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'sumo-page-heading'))
            )
            assert (
                'Add-on Badges'
                in page.driver.find_element(By.CLASS_NAME, 'sumo-page-heading').text
            )
            page.driver.switch_to.window(initial_window)
