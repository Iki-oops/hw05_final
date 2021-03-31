import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import forms
from django.urls import reverse

from posts.models import Group, Post, Follow


SMALL_GIF = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
)


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = get_user_model().objects.create_user(username='YaBobyor')
        cls.group = Group.objects.create(
            title='Тест',
            slug='test',
            description='Домашние тесты',
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='ya bobyor',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='YaBobr')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        template_pages_name = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts',
                                  args=[PostPagesTest.group.slug]),
            'new_post.html': reverse('new_post'),
            'profile.html': reverse('profile', args=[PostPagesTest.user])
        }

        for template, reverse_name in template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_list_show_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        get_page = response.context.get('page')[0]
        post_text_0 = get_page.text
        post_author_0 = get_page.author
        post_group_0 = get_page.group
        post_image_0 = get_page.image
        self.assertEquals(post_text_0, 'ya bobyor')
        self.assertEquals(post_author_0, PostPagesTest.user)
        self.assertEquals(post_group_0, PostPagesTest.group)
        self.assertTrue(post_image_0, PostPagesTest.uploaded)

    def test_post_view_show_correct_context(self):
        username = PostPagesTest.user.username
        post_id = PostPagesTest.post.id
        response = self.authorized_client.get(reverse('post', args=[username, post_id]))
        get_post = response.context.get('post')
        post_image = get_post.image
        self.assertTrue(post_image, PostPagesTest.uploaded)

    def test_new_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, excepted in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, excepted)

    def test_group_posts_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('group_posts', args=[PostPagesTest.group.slug]))
        get_group = response.context.get('group')
        get_post = response.context.get('page')[0]
        post_image = get_post.image
        group_title = get_group.title
        group_slug = get_group.slug
        group_description = get_group.description
        self.assertEquals(group_title, 'Тест')
        self.assertEquals(group_slug, 'test')
        self.assertEquals(group_description, 'Домашние тесты')
        self.assertTrue(post_image, PostPagesTest.uploaded)

    def test_profile_list_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', args=[PostPagesTest.user]))
        get_page = response.context.get('page')[0]
        profile_text_0 = get_page.text
        profile_author_0 = get_page.author
        profile_group_0 = get_page.group
        profile_image_0 = get_page.image
        self.assertEquals(profile_text_0, 'ya bobyor')
        self.assertEquals(profile_author_0, PostPagesTest.user)
        self.assertEquals(profile_group_0, PostPagesTest.group)
        self.assertTrue(profile_image_0, PostPagesTest.uploaded)

    def test_created_post_in_index(self):
        response = self.authorized_client.get(reverse('index'))
        post = PostPagesTest.post.group
        self.assertEquals(post, response.context.get('page')[0].group)

    def test_created_post_in_selected_group(self):
        response = self.authorized_client.get(
            reverse('group_posts', args=[PostPagesTest.group.slug]))
        post = PostPagesTest.post.group
        self.assertEquals(post, response.context.get('page')[0].group)

    # Тесты системы подписок
    def test_check_profile_follow(self):
        self.authorized_client.get(
            reverse('profile_follow', args=[PostPagesTest.user]))
        profile_response = self.authorized_client.get(
            reverse('profile', args=[PostPagesTest.user]))
        following = profile_response.context.get('following')
        follow = Follow.objects.get(user=self.user, author=PostPagesTest.user)
        self.assertTrue(following, follow)

    def test_check_profile_unfollow(self):
        self.authorized_client.get(
            reverse('profile_follow', args=[PostPagesTest.user]))
        self.authorized_client.get(
            reverse('profile_unfollow', args=[PostPagesTest.user]))
        profile_response = self.authorized_client.get(
            reverse('profile', args=[PostPagesTest.user]))
        following = profile_response.context.get('following')
        self.assertFalse(following)

    def test_following_post_in_follower_menu(self):
        another_user = get_user_model().objects.create_user(username='Ya')
        self.authorized_client.get(
            reverse('profile_follow', args=[PostPagesTest.user]))
        follow_index_response = self.authorized_client.get(
            reverse('follow_index'))
        posts = Post.objects.get(author=PostPagesTest.user)
        other_posts = Post.objects.create(
            author=another_user, text='test', group=PostPagesTest.group)
        follow_posts = follow_index_response.context.get('page')[0]
        self.assertEquals(follow_posts, posts)
        self.assertNotEquals(follow_posts, other_posts)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тест',
            slug='test',
            description='Домашние тесты',
        )
        cls.group = Group.objects.get(slug='test')
        cls.user = get_user_model().objects.create_user(username='Ya')
        for i in range(13):
            Post.objects.create(
                text='Ya',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_first_page_containse_ten_records(self):
        response = self.authorized_client.get(reverse('index'))
        get_page = response.context.get('page').object_list
        self.assertEquals(len(get_page), 10)

    def test_second_page_containse_three_records(self):
        response = self.authorized_client.get(reverse('index') + '?page=2')
        get_page = response.context.get('page').object_list
        self.assertEquals(len(get_page), 3)
