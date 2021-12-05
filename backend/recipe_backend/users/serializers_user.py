from django.utils import timezone
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipe_features.models import Follow
from users.models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    '''Serializing data for work with user and his profile'''
    date_joined = serializers.HiddenField(
        default=timezone.now)
    is_subscribed = serializers.SerializerMethodField(
        'get_subscribed', read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'id',
            'last_name', 'date_joined', 'is_subscribed')
        read_only_fields = ('date_joined', )
        ref_name = 'ReadOnlyUsers'

    def get_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()
