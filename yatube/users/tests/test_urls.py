from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup_url_exists_at_desired_location(self):
        """Провереряет, что URL-адреса существуют."""
        response = self.guest_client.get("/auth/signup/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "users:signup": "users/signup.html",
        }
        for url_name, template_name in templates_url_names.items():
            with self.subTest(template=template_name):
                url = reverse(url_name)
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template_name)
