from django.contrib import admin
from .models import Post, Group, Comment


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'description',
        'slug'
    )
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    empty_value_display = '-пусто-'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'post',
        'author',
        'created',
    )
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)