import unittest
from django.test import TestCase
from django.urls import reverse

from .views import CommentsMixin, CommentCreate, CommentList, CommentUpdate, CommentDelete, NewsList, NewsDetailView
from .forms import CommentForm
from .models import News, Comment
from .base import CommentBase

class TestViews(TestCase):
    fixtures = ['initial_data.json']
    
    def setUp(self):
        self.user = UserFactory().create()
        self.article = ArticleFactory().create()
        
    def test_list_view(self):
        response = NewsList.as_view()(request=self.client.get('/'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/list.html')
        self.assertEquals(len(response.context['object_list']), 10)
    
    def test_detail_view(self):
        response = NewsDetailView.as_view()(request=self.client.get('/{}/'.format(self.article.id)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/detail.html')
        self.assertEquals(response.context['object'], self.article)
        self.assertTrue('#comments' in response.content.decode())
    
    def test_create_form(self):
        response = CommentCreate.as_view()(request=self.client.post('/{}-comments/. '.format(self.article.id)), user=self.user)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/{}/'.format(self.article.id)) + '#comments'
    
    def test_update_form(self):
        comment = CommentFactory(news=self.article).create()
        response = CommentUpdate.as_view()(request=self.client.put('/{}-comments/{}. '.format(self.article.id, comment.id), data={'text': 'new text'}, user=self.user)).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'new text')
    
    def test_delete_view(self):
        comment = CommentFactory(news=self.article).create()
        response = CommentDelete.as_view()(request=self.client.delete('/{}-comments/{}. '.format(self.article.id, comment.id), user=self.user))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/{}/'.format(self.article.id)) + '#comments'
    
    def test_anonymous_cant_comment(self):
        response = self.client.post('/{}-comments/. '.format(self.article.id), {'text': 'a random comment.'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=%2F%7B%7Bi%7D-%7Bc%7D-.%7D')
    
    def test_bad_words(self):
        form = CommentForm({'text': 'redisca blahblah...!'})
        with self.assertRaisesMessage(ValidationError, WARNING):
            form.full_clean()