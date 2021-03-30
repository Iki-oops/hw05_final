import shutil
import tempfile

from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, Comment


class GroupCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = get_user_model().objects.create_user(username='Ya')
        cls.group = Group.objects.create(
            title='Yo-Yo',
            slug='yoyo',
            description='Yo-Yo is cool'
        )
        cls.post = Post.objects.create(
            text='Yo-Yo test text',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()
        cls.comment_form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(GroupCreateFormTest.user)

    def test_labels_postform(self):
        label_fields = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for value, expected in label_fields.items():
            with self.subTest(value=value):
                response = GroupCreateFormTest.form.fields[value].label
                self.assertEquals(response, expected)

    def test_create_post(self):
        posts_count = Post.objects.count()
        group = GroupCreateFormTest.group
        form_data = {
            'group': group.id,
            'text': 'Yo-Yo test',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.last(),
                        Post.objects.filter(
                            group=group.id, text='Yo-Yo test'))

    def test_changed_form_data(self):
        post = GroupCreateFormTest.post
        group = GroupCreateFormTest.group
        user = GroupCreateFormTest.user
        form_data = {
            'group': group.id,
            'text': 'Ya',
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit', kwargs={'username': user, 'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.last().text, 'Ya')
        self.assertEqual(Post.objects.last().group.id, group.id)
        self.assertRedirects(response, reverse('post', args=[user, post.id]))

    def test_only_authorized_user_can_comment(self):
        post_id = GroupCreateFormTest.post.id
        user = GroupCreateFormTest.user
        form_data = {
            'text': 'Вау',
        }
        self.authorized_client.post(
            reverse('post',
                    args=[user, post_id]),
            data=form_data,
        )
        self.assertEqual(Comment.objects.last().text, 'Вау')
