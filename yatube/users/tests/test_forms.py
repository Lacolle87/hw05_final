from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class CreationFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup(self):
        """Форма создает нового пользователя."""
        users_count = User.objects.count()
        form_data = {
            "first_name": "Bob",
            "last_name": "Rock",
            "username": "bob_rock",
            "email": "test@test.ru",
            "password1": "DjangoYandex",
            "password2": "DjangoYandex",
        }
        response = self.guest_client.post(
            reverse("users:signup"), data=form_data, follow=True
        )
        user = User.objects.last()
        self.assertRedirects(response, reverse("posts:index"))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(user.username, form_data['username'])
        self.assertEqual(user.first_name, form_data['first_name'])
        self.assertEqual(user.last_name, form_data['last_name'])
        self.assertEqual(user.email, form_data['email'])
