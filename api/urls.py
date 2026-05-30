from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Авторизація
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.UserLoginView.as_view(), name='login'),
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),

    # Оголошення
    path('announcements/', views.AnnouncementListCreateView.as_view(), name='announcement-list-create'),
    # Запис <int:pk> означає, що тут буде число (ID). Наприклад: /api/announcements/1/
    path('announcements/<int:pk>/', views.AnnouncementDetailView.as_view(), name='announcement-detail'),

    # Реакції (Коментарі та Лайки)
    path('comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('likes/toggle/', views.LikeToggleView.as_view(), name='like-toggle'),

    # Інформація про додаток
    path('info/', views.app_info_view, name='app-info'),
]