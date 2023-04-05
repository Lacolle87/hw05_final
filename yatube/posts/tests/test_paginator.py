from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User
from .constants import *


class PaginationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='BobRock',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание',
        )
        for i in range(15):
            Post.objects.create(
                text=f'Пост #{i}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()

    def test_pagination_on_pages(self):
        """Проверка пагинации на страницах."""
        posts_on_first_page = 10
        posts_on_second_page = 5
        urls = [
            reverse(INDEX_URL),
            reverse(GROUP_LIST_URL, kwargs={'slug': self.group.slug}),
            reverse(PROFILE_URL, kwargs={'username': self.user.username}),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context['page_obj']),
                                 posts_on_first_page)
                response = self.guest_client.get(f"{url}?page=2")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context['page_obj']),
                                 posts_on_second_page)
