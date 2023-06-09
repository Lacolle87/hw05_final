# Generated by Django 2.2.16 on 2023-04-08 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_comment_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',), 'verbose_name': 'комментарий', 'verbose_name_plural': 'комментарии'},
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('-author',)},
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_follow'),
        ),
    ]
