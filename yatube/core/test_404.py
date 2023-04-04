from http import HTTPStatus

from django.test import TestCase, Client


class Test404Class(TestCase):
    def setUp(self):
        """Создаем данные для тестирования"""
        super().setUp()
        # Создаем неавторизованного пользователя
        self.guest_client = Client()

    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_404(self):
        """Возвращается 404 для несуществующих URL"""
        url_status_dict = {
            '/404/': HTTPStatus.NOT_FOUND,
            '/group/404/': HTTPStatus.NOT_FOUND,
            '/profile/404/': HTTPStatus.NOT_FOUND,
            '/posts/404/': HTTPStatus.NOT_FOUND,
        }
        for url, status in url_status_dict.items():
            with self.subTest(url=url, status=status):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)
