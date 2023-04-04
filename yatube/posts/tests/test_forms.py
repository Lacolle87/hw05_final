from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class PostFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="BobRock")
        self.post = Post.objects.create(
            author=self.user,
            text="Тестовый текст",
        )
        self.group = Group.objects.create(
            title="Тестовое сообщество",
            slug="test-slug",
            description="Тестовое описание",
        )
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {"text": "Тестовый текс"}
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile",
                              kwargs={"username": self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text="Тестовый текст").exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Форма изменяет запись в Post."""
        posts_count = Post.objects.count()
        form_data = {"text": "Измененный текст", "group": self.group.id}
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        edited_post = Post.objects.get(id=self.post.id)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text="Изменяем текст").exists())
        self.assertEqual(edited_post.text, form_data["text"])
        self.assertEqual(edited_post.group.id, form_data["group"])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_not_create_guest_client(self):
        """Форма не изменит запись в Post если неавторизован."""
        posts_count = Post.objects.count()
        form_data = {"text": "Изменяем текст", "group": self.group.id}
        response = self.guest_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse("login") + "?next=" + reverse(
                "posts:post_edit", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text="Изменяем текст").exists())
        self.assertNotIn('group', response.context['form'].fields)
        self.assertEqual(response.status_code, HTTPStatus.OK)
