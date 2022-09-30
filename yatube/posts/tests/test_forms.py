from posts.models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name1'),
            text='Тестовая запись',
            group=Group.objects.create(
                title='Заголовок для тестовой группы',
                slug='test_slug'))

        cls.group = Group.objects.create(
            title='Лев Толстой',
            slug='test_slug10'
        )

        cls.author = User.objects.create_user(
            username='authorPosts')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Batman')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def test_form_create(self):
        """Проверка создания нового поста, авторизированным пользователем"""
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовая запись',
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': 'Batman'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Тестовая запись',
            group=TestCreateForm.group).exists())

    def test_form_edit(self):
        """Проверка редактирования поста через форму на странице"""
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': self.post.id,
        }
        response = self.authorized_author.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(
            text=self.post.id,
            group=TestCreateForm.group).exists())
        self.assertEqual(Post.objects.count(), post_count)
