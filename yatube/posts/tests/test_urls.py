from http import HTTPStatus

from django.urls import reverse
from django.test import Client, TestCase
from django.core.cache import cache

from posts.models import Post, Group, User, Comment
from .constants import (
    INDEX_URL,
    GROUP_LIST_URL,
    PROFILE_URL,
    POST_DETAIL_URL,
    POST_EDIT_URL,
    POST_CREATE_URL,
    ADD_COMMENT_URL,
    DELETE_COMMENT_URL,
    POST_FOLLOW_URL,
    POST_UNFOLLOW_URL,
    FOLLOW_INDEX_URL,
    GROUP_LIST_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_DETAIL_TEMPLATE,
    POST_CREATE_TEMPLATE,
)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="BobRock")
        cls.user2 = User.objects.create(username="JohnDoe")
        cls.group = Group.objects.create(
            title="Тест группа",
            slug="test-slug",
            description="Тест описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тест пост",
        )
        cls.templates = [
            reverse(INDEX_URL),
            reverse(GROUP_LIST_URL, kwargs={"slug": cls.group.slug}),
            reverse(PROFILE_URL, kwargs={"username": cls.user.username}),
            reverse(POST_DETAIL_URL, kwargs={"post_id": cls.post.id}),
        ]
        cls.templates_url_names = {
            reverse(INDEX_URL): "posts/index.html",
            reverse(
                GROUP_LIST_URL, kwargs={
                    "slug": cls.group.slug}): GROUP_LIST_TEMPLATE,
            reverse(
                PROFILE_URL, kwargs={
                    "username": cls.user.username}): PROFILE_TEMPLATE,
            reverse(
                POST_DETAIL_URL, kwargs={
                    "post_id": cls.post.id}): POST_DETAIL_TEMPLATE,
            reverse(POST_CREATE_URL): POST_CREATE_TEMPLATE,
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(template=template):
                cache.clear()
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location(self):
        """Провереряет, что URL-адреса существуют."""
        for address in self.templates:
            with self.subTest(address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_post_id_edit_url_exists_at_author(self):
        """Страница /posts/post_id/edit/ существует для автор."""
        response = self.authorized_client.get(
            reverse(POST_EDIT_URL, kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous_on_auth_login(self):
        """Страница /create/ для не авторизованного пользователя
        редирект на логин."""
        response = self.guest_client.get(
            reverse(POST_CREATE_URL), follow=True)
        self.assertRedirects(response, reverse(
            "login") + "?next=" + reverse(POST_CREATE_URL))

    def test_create_url_exists_for_authorized(self):
        """Страница /create/ существует для авторизованного пользователя."""
        response = self.authorized_client.get(reverse(POST_CREATE_URL))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_at_desired_location(self):
        """Несуществующая страница /unexisting_page/ должна выдать ошибку."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_detail_url_exists(self):
        """Страница /posts/post_id/ существует."""
        response = self.guest_client.get(
            reverse(POST_DETAIL_URL, kwargs={"post_id": self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_detail_url_exists(self):
        """Страница /group/group_list/ существует."""
        response = self.guest_client.get(
            reverse(GROUP_LIST_URL, kwargs={"slug": self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists(self):
        """Страница /profile/ существует."""
        response = self.guest_client.get(
            reverse(PROFILE_URL, kwargs={"username": self.user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_comment_url(self):
        """Тест что add_comment URL доступен."""
        response = self.authorized_client.get(
            reverse(ADD_COMMENT_URL, kwargs={"post_id": self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_comment_delete_url(self):
        """Тест что comment_delete URL доступен."""
        comment = Comment.objects.create(author=self.user, post=self.post,
                                         text="Тест комментарий")
        response = self.authorized_client.get(
            reverse(DELETE_COMMENT_URL, kwargs={"comment_id": comment.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_follow_index_url(self):
        """Тест что follow_index URL доступен."""
        response = self.authorized_client.get(reverse(FOLLOW_INDEX_URL))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_follow_url(self):
        """Тест что profile_follow URL доступен."""
        response = self.authorized_client.get(
            reverse(POST_FOLLOW_URL,
                    kwargs={"username": self.user2.username}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_profile_unfollow_url(self):
        """Тест что profile_unfollow URL доступен."""
        response = self.authorized_client.get(
            reverse(
                POST_UNFOLLOW_URL ,
                kwargs={"username": self.user2.username}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
