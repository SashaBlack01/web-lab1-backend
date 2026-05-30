from django.contrib import admin
from .models import Comment, Like

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__email']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'user', 'created_at']
    list_filter = ['created_at']