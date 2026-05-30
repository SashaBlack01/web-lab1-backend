from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from announcements.models import Announcement
from reactions.models import Comment, Like

User = get_user_model()

# ==========================================
# СЕРІАЛІЗАТОРИ ДЛЯ КОРИСТУВАЧІВ (АВТОРИЗАЦІЯ)
# ==========================================

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Серіалізатор для реєстрації користувача"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'gender', 'birth_date', 'password',
                  'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Паролі не співпадають")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        # Використовуємо create_user, щоб пароль автоматично зашифрувався (хешування)
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Серіалізатор для входу користувача"""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Невірний email або пароль')
            if not user.is_active:
                raise serializers.ValidationError('Акаунт деактивовано')
            data['user'] = user
        else:
            raise serializers.ValidationError('Необхідно вказати email та пароль')
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Серіалізатор для профілю (щоб віддавати дані про автора оголошення)"""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'gender', 'birth_date', 'avatar', 'bio']
        read_only_fields = ['id', 'email']


# ==========================================
# СЕРІАЛІЗАТОРИ ДЛЯ ОГОЛОШЕНЬ ТА РЕАКЦІЙ
# ==========================================

class CommentSerializer(serializers.ModelSerializer):
    """Серіалізатор для коментарів"""
    author = UserProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'announcement', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    """Серіалізатор для оголошень"""
    author = UserProfileSerializer(read_only=True)
    # Створюємо додаткові поля для підрахунку лайків та коментарів
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'author', 'image', 'likes_count', 'comments_count', 'created_at',
                  'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    # Функції для обчислення кількості реакцій
    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class LikeSerializer(serializers.ModelSerializer):
    """Серіалізатор для лайків"""

    class Meta:
        model = Like
        fields = ['announcement']

    def create(self, validated_data):
        # Автор лайка автоматично береться з поточного авторизованого користувача
        validated_data['user'] = self.context['request'].user

        # Логіка Toggle: якщо лайк вже стоїть - видаляємо, якщо немає - ставимо
        like, created = Like.objects.get_or_create(
            announcement=validated_data['announcement'],
            user=validated_data['user']
        )
        if not created:
            like.delete()
            return None  # Лайк знято
        return like