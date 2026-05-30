from django.db import models
from django.conf import settings
from announcements.models import Announcement

class Comment(models.Model):
    """Модель текстового коментаря до оголошення"""

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Оголошення'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    content = models.TextField(verbose_name='Текст коментаря')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')

    class Meta:
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'
        ordering = ['created_at']  # Старі коментарі зверху, нові знизу

    def __str__(self):
        return f"Комент від {self.author.full_name} до '{self.announcement.title}'"


class Like(models.Model):
    """Модель лайка до оголошення"""

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Цей параметр гарантує, що один юзер може поставити лише один лайк одному посту
        unique_together = ('announcement', 'user')
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'