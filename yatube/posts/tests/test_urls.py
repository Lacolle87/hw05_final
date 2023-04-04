from http import HTTPStatus

from django.urls import reverse
from django.test import Client, TestCase
from django.core.cache import cache

from posts.models import Post, Group, User, Comment


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
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": cls.group.slug}),
            reverse("posts:profile", kwargs={"username": cls.user.username}),
            reverse("posts:post_detail", kwargs={"post_id": cls.post.id}),
        ]
        cls.templates_url_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={
                    "slug": cls.group.slug}): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={
                    "username": cls.user.username}): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={
                    "post_id": cls.post.id}): "posts/post_detail.html",
            reverse("posts:post_create"): "posts/create_post.html",
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
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous_on_auth_login(self):
        """Страница /create/ для не авторизованного пользователя
        редирект на логин."""
        response = self.guest_client.get(
            reverse("posts:post_create"), follow=True)
        self.assertRedirects(response, reverse(
            "login") + "?next=" + reverse("posts:post_create"))

    def test_create_url_exists_for_authorized(self):
        """Страница /create/ существует для авторизованного пользователя."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_at_desired_location(self):
        """Несуществующая страница /unexisting_page/ должна выдать ошибку."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_detail_url_exists(self):
        """Страница /posts/post_id/ существует."""
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_detail_url_exists(self):
        """Страница /group/group_list/ существует."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists(self):
        """Страница /profile/ существует."""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_comment_url(self):
        """Тест что add_comment URL доступен."""
        response = self.authorized_client.get(
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_comment_delete_url(self):
        """Тест что comment_delete URL доступен."""
        comment = Comment.objects.create(author=self.user, post=self.post,
                                         text="Тест комментарий")
        response = self.authorized_client.get(
            reverse("posts:delete_comment", kwargs={"comment_id": comment.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_follow_index_url(self):
        """Тест что follow_index URL доступен."""
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_follow_url(self):
        """Тест что profile_follow URL доступен."""
        response = self.authorized_client.get(
            reverse("posts:profile_follow",
                    kwargs={"username": self.user2.username}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_profile_unfollow_url(self):
        """Тест что profile_unfollow URL доступен."""
        response = self.authorized_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.user2.username}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
