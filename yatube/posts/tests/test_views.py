import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings
from django import forms
from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, User, Follow, Comment
from .constants import *

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="BobRock")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )
        cls.templates_pages_names = {
            reverse(INDEX_URL): INDEX_TEMPLATE,
            reverse(
                GROUP_LIST_URL, kwargs={"slug": cls.group.slug}
            ): GROUP_LIST_TEMPLATE,
            reverse(
                PROFILE_URL, kwargs={"username": cls.post.author}
            ): PROFILE_TEMPLATE,
            reverse(
                POST_DETAIL_URL, kwargs={"post_id": cls.post.id}
            ): POST_DETAIL_TEMPLATE,
            reverse(
                POST_EDIT_URL, kwargs={"post_id": cls.post.id}
            ): POST_EDIT_TEMPLATE,
            reverse(POST_CREATE_URL): POST_CREATE_TEMPLATE,
        }

    def assertFormFieldsType(self, response, form_fields):
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.group = PostPagesTests.group
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=PostPagesTests.user,
            group=self.group,
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=PostPagesTests.user,
            text='Тест'
        )
        self.guest_client = Client()

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовые медиа."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, reverse_name)

    def test_index_show_correct_context(self):
        """Список постов в шаблоне index равен ожидаемому контексту."""
        cache.clear()
        response = self.guest_client.get(reverse(INDEX_URL))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['page_obj'],
                                 Post.objects.all()[:10],
                                 transform=lambda x: x)

    def test_group_list_show_correct_context(self):
        """Список постов в шаблоне group_list равен ожидаемому контексту."""
        response = self.guest_client.get(
            reverse(GROUP_LIST_URL, kwargs={"slug": self.group.slug})
        )
        expected_queryset = Post.objects.filter(group_id=self.group.id)[:10]
        self.assertQuerysetEqual(response.context["page_obj"],
                                 expected_queryset, transform=lambda x: x)

    def test_profile_show_correct_context(self):
        """Список постов в шаблоне profile равен ожидаемому контексту."""
        response = self.guest_client.get(
            reverse(PROFILE_URL, args=(self.post.author,))
        )
        expected = Post.objects.filter(author=self.user)[:10]
        self.assertQuerysetEqual(
            response.context["page_obj"], expected, transform=lambda x: x
        )

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(POST_DETAIL_URL, kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.context.get("post").text, self.post.text)
        self.assertEqual(response.context.get("post").author, self.post.author)
        self.assertEqual(response.context.get("post").group, self.post.group)
        self.assertEqual(response.context.get("post").image, self.post.image)

    def test_create_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(POST_EDIT_URL, kwargs={"post_id": self.post.id})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        self.assertFormFieldsType(response, form_fields)

    def test_create_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(POST_CREATE_URL))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        self.assertFormFieldsType(response, form_fields)

    def test_check_group_in_pages(self):
        """Проверяем создание поста на страницах с выбранной группой"""
        form_fields = {
            reverse(INDEX_URL): self.post,
            reverse(GROUP_LIST_URL,
                    kwargs={"slug": self.group.slug}): self.post,
            reverse(PROFILE_URL,
                    kwargs={"username": self.user.username}): self.post,
        }
        cache.clear()
        for url, post in form_fields.items():
            with self.subTest(value=url):
                response = self.client.get(url)
                page_obj = response.context["page_obj"]
                self.assertIn(post, page_obj.object_list)

    def test_check_group_not_in_mistake_group_list_page(self):
        """Проверяем чтобы созданный Пост с группой не попал в чужую группу."""
        form_fields = {
            reverse(
                GROUP_LIST_URL, kwargs={"slug": self.group.slug}
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context["page_obj"]
                self.assertNotIn(expected, form_field)

    def test_comments_allowed_to_auth_user_only(self):
        """Комментировать может только авторизованный пользователь."""
        self.comment_data = {'text': 'test_comment'}
        self.guest_client.post(
            reverse(ADD_COMMENT_URL, kwargs={'post_id': self.post.id}),
            self.comment_data)
        response = self.guest_client.get(
            reverse(POST_DETAIL_URL, args=[self.post.id]))
        self.assertNotContains(
            response,
            self.comment_data['text'],
            status_code=HTTPStatus.OK
        )

    def test_comment_post_and_check(self):
        """После успешной отправки комментарий появляется на странице поста."""
        response = self.guest_client.get(
            reverse(POST_DETAIL_URL, args=[self.post.id]))
        self.assertContains(
            response, self.comment.text, status_code=HTTPStatus.OK)

    def test_cache_index(self):
        """Проверка кэша главной страницы."""
        response = self.authorized_client.get(reverse(INDEX_URL))
        self.assertContains(response, self.post, status_code=HTTPStatus.OK)
        self.post.delete()
        response2 = self.authorized_client.get(reverse(INDEX_URL))
        self.assertContains(response2, self.post, status_code=HTTPStatus.OK)
        cache.clear()
        response3 = self.authorized_client.get(reverse(INDEX_URL))
        self.assertNotContains(response3, self.post, status_code=HTTPStatus.OK)


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(
            username='JohnDoe')
        cls.second_user = User.objects.create_user(
            username='IvanDrago')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(
            user=cls.second_user,
            author=cls.author,
        )

    def setUp(self):
        self.first_authorized_client = Client()
        self.first_authorized_client.force_login(FollowViewTest.first_user)
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(
            FollowViewTest.second_user)

    def test_user_follow_to_author(self):
        """
        Пользователь подписался на автора.
        """
        count_follow = Follow.objects.filter(user=self.first_user).count()
        data_follow = {'user': self.first_user,
                       'author': self.author}
        redirect = reverse(
            PROFILE_URL,
            kwargs={'username': self.author.username}
        )
        response = self.first_authorized_client.post(
            reverse(POST_FOLLOW_URL,
                    kwargs={'username': self.author.username}),
            data=data_follow,
            follow=True)
        new_count_follow = Follow.objects.filter(
            user=self.first_user).count()
        self.assertTrue(Follow.objects.filter(
            user=self.first_user,
            author=self.author).exists())
        self.assertRedirects(response, redirect)
        self.assertEqual(count_follow + 1, new_count_follow)

    def test_user_unfollow_to_author(self):
        """
        Пользователь отписался от автора.
        """
        count_follow = Follow.objects.filter(user=self.second_user).count()
        data_follow = {'user': self.second_user,
                       'author': self.author}
        redirect = reverse(
            PROFILE_URL,
            kwargs={'username': self.author.username}
        )
        response = self.second_authorized_client.post(
            reverse(POST_UNFOLLOW_URL,
                    kwargs={'username': self.author.username}),
            data=data_follow,
            follow=True)
        new_count_unfollow = Follow.objects.filter(
            user=self.second_user).count()
        self.assertFalse(Follow.objects.filter(
            user=self.second_user,
            author=self.author).exists())
        self.assertRedirects(response, redirect)
        self.assertNotEqual(count_follow, new_count_unfollow)

    def test_follower_new_post(self):
        """
        У подписчика появляется новый пост избранного автора.
        """
        new_post_follower = Post.objects.create(
            author=self.author,
            text='test_text')
        Follow.objects.create(user=self.first_user,
                              author=self.author)
        response = self.first_authorized_client.get(
            reverse(FOLLOW_INDEX_URL))
        new_posts = response.context['page_obj']
        self.assertIn(new_post_follower, new_posts)

    def test_unfollower_new_post(self):
        """
        Новый пост не появляется у пользователя, который не подписан.
        """
        new_post_follower = Post.objects.create(
            author=self.first_user,
            text='other_test_text')
        Follow.objects.create(user=self.second_user,
                              author=self.author)
        response = self.second_authorized_client.get(
            reverse(FOLLOW_INDEX_URL))
        new_post_unfollower = response.context['page_obj']
        self.assertNotIn(new_post_follower, new_post_unfollower)
