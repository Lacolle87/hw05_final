from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Название сообщества', max_length=200)
    slug = models.SlugField('Ссылка сообщества', unique=True)
    description = models.TextField('Описание сообщества', max_length=400)

    class Meta:
        verbose_name = 'сообщество'
        verbose_name_plural = 'сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    objects = None
    text = models.TextField('Текст записи')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='group_posts',
        verbose_name='Сообщество',
        help_text='Укажите название вашего сообщества'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'запись'
        verbose_name_plural = 'записи'


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True,
                             related_name='comments')
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Введите текст комментария')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор')
    created = models.DateTimeField(verbose_name='Дата создания',
                                   auto_now_add=True)

    class Meta:
        ordering = ["-created"]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower'
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following'
                               )

    class Meta:
        ordering = ["-author"]
