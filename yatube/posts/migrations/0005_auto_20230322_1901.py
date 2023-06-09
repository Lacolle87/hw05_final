# Generated by Django 2.2.16 on 2023-03-22 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20230310_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Укажите название вашего сообщества', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_posts', to='posts.Group', verbose_name='Сообщество'),
        ),
    ]
