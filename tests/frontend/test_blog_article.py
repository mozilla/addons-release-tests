import time

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.frontend.blog_article import ArticlePage
from pages.desktop.frontend.blog_homepage import BlogHomepage
from pages.desktop.frontend.home import Home


@pytest.mark.nondestructive
def test_article_loaded_correctly(base_url, selenium, variables):
    selenium.get(f'{base_url}/blog/{variables["blog_article"]}/')
    page = ArticlePage(selenium, base_url)
    assert page.header_logo
    assert page.title
    assert page.author.name
    assert page.author.picture
    assert page.author.twitter_link
    assert page.author.pocket_link
    for link in page.nav_bar_links:
        assert link.is_displayed()
    # verify that the article has at least one paragraph
    assert page.content_paragraphs[0].is_displayed()
    # verify that at least one of next/prev article links is displayed
    try:
        assert page.next_article.is_displayed()
    except NoSuchElementException:
        page.previous_article.is_displayed()


@pytest.mark.nondestructive
def test_article_page_header_logo_button(base_url, selenium, variables):
    selenium.get(f'{base_url}/blog/{variables["blog_article"]}/')
    page = ArticlePage(selenium, base_url)
    page.header_logo.click()
    homepage = Home(selenium, base_url)
    assert homepage.primary_hero.is_displayed()


@pytest.mark.nondestructive
def test_navbar_frontend_homepage_link(base_url, selenium, variables):
    selenium.get(f'{base_url}/blog/{variables["blog_article"]}/')
    page = ArticlePage(selenium, base_url)
    page.nav_bar_links[0].click()
    homepage = Home(selenium, base_url)
    assert homepage.primary_hero.is_displayed()


@pytest.mark.nondestructive
def test_navbar_blog_homepage_link(base_url, selenium, variables):
    selenium.get(f'{base_url}/blog/{variables["blog_article"]}/')
    page = ArticlePage(selenium, base_url)
    page.nav_bar_links[1].click()
    blog_homepage = BlogHomepage(selenium, base_url)
    assert blog_homepage.articles[0].title.is_displayed()


@pytest.mark.nondestructive
def test_navbar_current_article_link(base_url, selenium, variables):
    selenium.get(f'{base_url}/blog/{variables["blog_article"]}/')
    page = ArticlePage(selenium, base_url)
    page.nav_bar_links[2].click()
    assert selenium.current_url in f'{base_url}/blog/{variables["blog_article"]}/'


@pytest.mark.nondestructive
def test_next_and_previous_article_links(base_url, selenium, variables):
    selenium.get(f'{base_url}/blog/{variables["blog_article"]}/')
    page = ArticlePage(selenium, base_url)
    initial_title = page.title.text
    page.next_article.click()
    page.previous_article.click()
    assert initial_title in page.title.text


@pytest.mark.nondestructive
def test_addon_card_recommendation_badge_link(base_url, selenium, variables):
    selenium.get(f'{base_url}/blog/{variables["blog_article"]}/')
    page = ArticlePage(selenium, base_url)
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
