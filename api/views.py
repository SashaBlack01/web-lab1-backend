from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from announcements.models import Announcement
from reactions.models import Comment
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    AnnouncementSerializer, CommentSerializer, LikeSerializer
)

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """Реєстрація нового користувача"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Доступно всім (навіть неавторизованим)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Автоматично створюємо токен при реєстрації
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """Вхід користувача в систему"""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Отримання та редагування профілю поточного користувача"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # Тільки для авторизованих

    def get_object(self):
        # Повертає юзера, який відправив цей запит (визначається за токеном)
        return self.request.user



class AnnouncementListCreateView(generics.ListCreateAPIView):
    """Список усіх оголошень або створення нового"""
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Announcement.objects.all()

    def perform_create(self, serializer):
        # Під час створення оголошення автоматично ставимо автором поточного юзера
        serializer.save(author=self.request.user)


class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Перегляд, оновлення або видалення конкретного оголошення"""
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Announcement.objects.all()



class CommentListCreateView(generics.ListCreateAPIView):
    """Список коментарів до конкретного оголошення та створення коментаря"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Дозволяє фільтрувати коментарі, передаючи ?announcement=1 у посиланні
        announcement_id = self.request.query_params.get('announcement')
        if announcement_id:
            return Comment.objects.filter(announcement_id=announcement_id)
        return Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class LikeToggleView(generics.CreateAPIView):
    """Поставити або зняти лайк з оголошення"""
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Передаємо об'єкт request у серіалізатор, щоб він знав, хто ставить лайк
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        like = serializer.save()

        if like is None:
            return Response({"message": "Лайк успішно знято"}, status=status.HTTP_200_OK)
        return Response({"message": "Лайк успішно поставлено"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def app_info_view(request):
    """Ендпоінт з базовою інформацією про додаток"""
    return Response({
        'name': 'Канал оголошень (Announcement Board)',
        'version': '1.0.0',
        'description': 'Платформа для публікації оголошень, обміну цифровим контентом та коментування записів у реальному часі.',
        'features': [
            'Реєстрація та JWT авторизація',
            'Стрічка оголошень',
            'Система коментарів та лайків'
        ],
        'author': 'Олександр Чернишков КВ-51мн',
    })