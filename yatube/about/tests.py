from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class AboutTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exists_at_desired_location(self):
        """Провереряет, что URL-адреса существуют."""
        templates = ["/about/author/", "/about/tech/"]
        for adress in templates:
            with self.subTest(adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/about/author/": "about/author.html",
            "/about/tech/": "about/tech.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_about_page_accessible_by_name(self):
        """Генерируемые URL доступы."""
        templates_url = ["about:author", "about:tech"]
        for adress in templates_url:
            with self.subTest(adress):
                response = self.guest_client.get(reverse(adress))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates = {
            "about:author": "about/author.html",
            "about:tech": "about/tech.html",
        }
        for adress, url in templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(adress))
                self.assertTemplateUsed(response, url)
