from django.test import Client, TestCase
from django.urls import reverse


class UsersViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """Генерируемые URL доступен."""
        response = self.guest_client.get(reverse("users:signup"))
        self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.guest_client.get(reverse("users:signup"))
        self.assertTemplateUsed(response, "users/signup.html")
