import time
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from http import HTTPStatus

from django.test import TestCase
# Импортируем функцию reverse().
from django.urls import reverse

from news.views import *
from news.forms import *


class MyLiveServerTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server = HTTPServer(('localhost', 8000), HomePage)
        cls.url = "http://localhost:{}".format(cls.server.socket.getsockname()[1])
        cls.browser = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        cls.server.shutdown()
        super().tearDownClass()


class TestRoutes(TestCase):

    def test_home_page(self):
        # Вместо прямого указания адреса 
        # получаем его при помощи функции reverse().
        url = reverse('news:home')
        response = self.client.get(url)
        # Проверяем, что код ответа равен статусу OK (он же 200).
        self.assertEqual(response.status_code, HTTPStatus.OK) 

class BaseTestViews(unittest.TestCase):
    fixtures = ['news.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("johndoe", "password")

    
    def test_homepage_anonymous(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_details_page_anonymous(self):
        news = News.objects.first()
        response = self.client.get("/news/{}/".format(news.id))
        self.assertEqual(response.status_code, 200)

    def test_delete_comment_authorized(self):
        comment = Comment.objects.create(news=News.objects.last(), author=self.user, text="My first comment!")
        delete_url = reverse("delete", args=(comment.id,))
        login(self.client, username="johndoe", password="password")
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)

    def test_edit_comment_authorized(self):
        comment = Comment.objects.create(news=News.objects.last(), author=self.user, text="My first comment!")
        edit_url = reverse("edit", args=(comment.id,))
        login(self.client, username="johndoe", password="password")
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)

    def test_delete_comment_not_allowed(self):
        comment = Comment.objects.create(news=News.objects.last(), author=User.objects.first())
        delete_url = reverse("delete", args=(comment.id,))
        login(self.client, username="otheruser", password="password")
        response = self.client.get(delete_url)
        self.assertRedirects(response, "/login?next=%s" % delete_url, status_codes=[302], msg_prefix="Login required.")

    def test_register(self):
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'password',
            'password2': 'password',
        }, follow=true)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.exists())

    def test_login(self):
        user = User.objects.create_user('myuser', 'mypassword')
        self.client.login(username='myuser', password='mypassword')
        self.assertIn('logout', self.client.session)

    def test_logout(self):
        self.client.login(username='myuser', password='mypassword')
        logout_url = '/accounts/logout/'
        response = self.client.get(logout_url)
        self.assertNotIn('logout', self.client.session)

    def test_search(self):
        search_term = "Python"
        query = Q(title__icontains=search_term)|Q(content__icontains=search_term)
        results = list(News.objects.filter(query).distinct().order_by("-pub_date"))[:5]
        for result in results:
            response = self.client.get(reverse("detail", args=(result.pk,)))
            self.assertEqual(response.context["object"] == result)
            
    def test_upload(self):
        data = {'file': open("path/to/image.jpg", 'rb'), }
        url = reverse("upload")
        response = self.client.post(url, data, follow=True)
        # The browser will be automatically closed at the end of this block
        self.browser.find_element_by_link_text("Home").click()
        time.sleep(1)
        self.browser.switch_to.window(self.browser.current_window_handle)
        page_source = self.browser.page_source
        assert b'<img src="/media/images/image.jpg">' in page_source


# A simple test that validates an existing view and ensures it returns a correct response when accessed via the client.
def test_about_view():
    response = client.get(reverse("about"))
    assert response.status_code == 200
    assert "About Page" in response.content.decode()