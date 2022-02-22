import pytest
from selenium.webdriver.common.by import By

from pages.desktop.frontend.blog_article import ArticlePage
from pages.desktop.frontend.blog_homepage import BlogHomepage
from pages.desktop.frontend.home import Home


@pytest.mark.nondesstructive
def test_blog_homepage_header_logo_button(base_url, selenium):
    page = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    page.header.click_title()
    homepage = Home(selenium, base_url)
    assert homepage.primary_hero.is_displayed()


@pytest.mark.nondesstructive
def test_articles_elements_are_displayed(base_url, selenium):
    page = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    for article in page.articles:
        assert article.image.is_displayed()
        assert article.title.is_displayed()
        assert article.date.is_displayed()
        assert article.intro_text.is_displayed()
        assert article.read_more_link.is_displayed()


@pytest.mark.nondesstructive
def test_open_article_by_clicking_article_image(base_url, selenium):
    page = BlogHomepage(selenium, base_url).open().wait_for_page_to_load()
    article_title = page.articles[0].title.text
    page.articles[0].image.click()
    article_page = ArticlePage(selenium, base_url)
    assert article_title.lower() in article_page.title.text.lower()


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
