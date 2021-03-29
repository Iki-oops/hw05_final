from django.test import TestCase, Client


class StaticPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_urls(self):
        urls = {
            'author': '/about/author/',
            'tech': '/about/tech/',
        }
        for value in urls.values():
            with self.subTest(value=value):
                response = self.guest_client.get(value)
                self.assertEquals(response.status_code, 200)
