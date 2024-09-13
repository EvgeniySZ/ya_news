class TestCommentLogic(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.author = UserFactory(username='test_author').create()
        cls.article = ArticleFactory(title="Test article", content="This is a test article.", author=cls.author).create()

    def setUp(self):
        self.client.force_login(self.author)

    def test_anonymous_cannot_submit_comment(self):
        response = self.client.post("/{}-comments/".format(self.article.id), {"text": "A random comment."}, follow=True)
        self.assertEqual(response.status_code, redirect('login').value)
        # Check that login page was displayed correctly
        self.assertContains(response, "<input type=\"email\" name=\"login\" placeholder=\"Email Address\")")

    def test_authenticated_can_submit_comment(self):
        response = self.client.post("/{}-comments/".format(self.article.id), {"text": "A new comment"}, follow=True)
        self.assertEqual(response.status_code, redirect("{}-comments/".format(self.article.id)).value)
        self.assertContains(response, '<div class="alert alert-success">Your comment has been submitted successfully.</div>', html=True)

    def test_forbidden_word_in_comment(self):
        form = CommentForm({"text": "Redisca blahblah..."})
        with self.assertRaisesMessage(ValidationError, "WARNING"):
            form.full_clean()

    def test_authorized_user_edits_own_comment(self):
        comment = CommentFactory(news=self.article, author=self.author).create()
        updated_text = "Updated comment!"
        response = self.client.put("/{}-comments/{}/".format(self.article.id, comment.id), {"text": updated_text}, follow=True)
        self.assertEqual(response.status_code, redirect("{}-comments/".format(self.article.id)).value)
        self.assertContains(response, '<h4>Updated comment!</h4>', html=True)

    def test_authorized_user_deletes_own_comment(self):
        comment = CommentFactory(news=self.article, author=self.author).create()
        response = self.client.delete("/{}-comments/{}/".format(self.article.id, comment.id), follow=True)
        self.assertEqual(response.status_code, redirect("{}-comments/".format(self.article.id)).value)
        self.assertContains(response, '<p class="alert alert-danger">Your comment has been deleted.</p>', html=True)

    def test_unauthorized_user_cannot_edit_or_delete_others_comment(self):
        other_user = UserFactory().create()
        other_user_comment = CommentFactory(news=self.article, author=other_user).create()
        # Attempting to edit another user's comment
        response = self.client.put("/{}-comments/{}/".format(self.article.id, other_user_comment.id), {"text": "New text"}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertContains(response, '<h1>Forbidden</h1><hr/>', html=True)

        # Attempting to delete another user's comment
        response = self.client.delete("/{}-comments/{}/".format(self.article.id, other_user_comment.id), follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertContains(response, '<h1>Forbidden</h1><hr/>', html=True)