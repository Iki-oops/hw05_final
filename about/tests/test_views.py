from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_accessible_by_name(self):
        pages_accessible = {
            'author': 'about:author',
            'tech': 'about:tech',
        }
        for value in pages_accessible.values():
            with self.subTest(value=value):
                response = self.guest_client.get(reverse(value))
                self.assertEqual(response.status_code, 200)

    def test_pages_uses_correct_template(self):
        templates = {
            'about/author.html': 'about:author',
            'about/tech.html': 'about:tech',
        }
        for template, value in templates.items():
            with self.subTest(value=value):
                response = self.guest_client.get(reverse(value))
                self.assertTemplateUsed(response, template)
