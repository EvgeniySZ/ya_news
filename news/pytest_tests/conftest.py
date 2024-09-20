import pytest
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone
import pytz

from news.models import Comment, News

User = get_user_model()

@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')

@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')

@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client

@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client

@pytest.fixture
def note(author):
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        slug='note-slug',
        author=author,
    )

@pytest.fixture
def news_data(db):
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news

@pytest.fixture
def detail_news(db):
    news = News.objects.create(
        title='Тестовая новость', text='Просто текст.'
    )
    author = User.objects.create(username='Комментатор')
    tz = pytz.timezone('Europe/Moscow')
    now = timezone.now().astimezone(tz)

    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()

    return news, author
