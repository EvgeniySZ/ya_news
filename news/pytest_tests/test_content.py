from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from news.forms import CommentForm

User = get_user_model()


@pytest.mark.django_db
def test_news_count(client, news_data):
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_data):
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_news):
    news, _ = detail_news
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, detail_news):
    news, author = detail_news
    client.force_login(author)
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_comments_order(client, detail_news):
    news, _ = detail_news
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
