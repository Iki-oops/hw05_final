from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Оглавление',
                             help_text='Оглавление группы')
    slug = models.SlugField(unique=True, verbose_name='URL',
                            help_text='URL для группы')
    description = models.TextField(verbose_name='Описание',
                                   help_text='Описание группы')

    class Meta:
        verbose_name_plural = 'Сообщества'
        verbose_name = 'Сообщество'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст',
                            help_text='Текст поста')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор', related_name='posts',
                               help_text='Автор поста')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True,
                              verbose_name='Группа', related_name='posts',
                              null=True, help_text='Ссылка на группу')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Пост', related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор', related_name='comments')
    text = models.TextField(verbose_name='Комментарий',
                            help_text='Текст комментария')
    created = models.DateTimeField('created', auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Follower', related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique follow')
        ]
