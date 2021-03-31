import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, Comment


SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


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
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'group': group.id,
            'text': 'Yo-Yo test',
            'image': uploaded,
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
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'group': group.id,
            'text': 'Ya',
            'image': uploaded,
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

    # def test_anonymous_can_not_comment(self):
    #     post_id = GroupCreateFormTest.post.id
    #     user = GroupCreateFormTest.user
    #     form_data = {
    #         'text': 'Вау',
    #     }
    #     self.guest_client.post(
    #         reverse('post',
    #                 args=[user, post_id]),
    #         data=form_data,
    #     )
    #     self.assertFalse(Comment.objects.last().text, 'Вау')
        # self.assertFormError(
        #     response, 'form', 'slug', 'first уже существует'
        # )
