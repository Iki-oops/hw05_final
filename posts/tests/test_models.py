from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Post, Group


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = get_user_model().objects.create_user(username='Ya_bober')
        cls.group = Group.objects.create(
            title='church',
            slug='churches',
            description='bread',
        )

        cls.post = Post.objects.create(
            text='crush',
            author=user,
            group=cls.group,
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verbose = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEquals(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_help_text = {
            'text': 'Текст поста',
            'group': 'Ссылка на группу',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEquals(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field(self):
        group = PostModelTest.group
        expected_object_name = 'church'
        self.assertEquals(group.title, expected_object_name)

    def test_object_name_is_text_field(self):
        post = PostModelTest.post
        expected_object_name = 'crush'
        self.assertEquals(post.text, expected_object_name)
