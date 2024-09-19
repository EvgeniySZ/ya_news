import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def setup_data(db):
    news = News.objects.create(title='Заголовок', text='Текст')
    author = User.objects.create(username='Лев Толстой')
    reader = User.objects.create(username='Читатель простой')
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return {
        'news': news,
        'author': author,
        'reader': reader,
        'comment': comment,
    }


@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(client, setup_data):
    author = setup_data['author']
    reader = setup_data['reader']
    comment = setup_data['comment']

    users_statuses = (
        (author, HTTPStatus.OK),
        (reader, HTTPStatus.NOT_FOUND),
    )

    for user, expected_status in users_statuses:
        client.force_login(user)
        for name in ('news:edit', 'news:delete'):
            url = reverse(name, args=(comment.id,))
            response = client.get(url)
            assert response.status_code == expected_status


@pytest.mark.django_db
def test_pages_availability(client, setup_data):
    urls = (
        ('news:home', None),
        ('news:detail', (setup_data['news'].id,)),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )

    for name, args in urls:
        url = reverse(name, args=args)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, setup_data):
    login_url = reverse('users:login')
    comment = setup_data['comment']

    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == redirect_url
