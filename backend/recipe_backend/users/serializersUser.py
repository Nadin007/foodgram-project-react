from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, serializers
from rest_framework.validators import UniqueValidator

from recipe_features.models import Follow
from users.models import User


class ConfirmationTokenSerializer(serializers.Serializer):
    '''Serializing verification data to provide full user registration'''

    password = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)

    def validate(self, request):
        self.validate_new_password(request)
        return super().validate(request)

    def validate_new_password(self, value):
        email = value['email']
        password = value['password']
        user = generics.get_object_or_404(
                User, email=email
            )
        if not check_password(password, user.password):
            raise serializers.ValidationError(
                _('That is not the correct Password.')
            )
        return password


class UserSerializer(serializers.ModelSerializer):
    '''Serializing data for work with user and his profile'''
    email = serializers.EmailField(
        required=True, max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        required=True, max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, max_length=150,
                                     write_only=True)
    date_joined = serializers.HiddenField(
        default=timezone.now)
    is_subscribed = serializers.SerializerMethodField(
        'get_subscribed', read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'id',
            'last_name', 'password', 'avatar', 'date_joined', 'is_subscribed')
        read_only_fields = ('date_joined', )
        ref_name = 'ReadOnlyUsers'

    def validate(self, data):
        if data["username"] == 'me':
            raise serializers.ValidationError("User can't be called 'me'")
        username = data['username']
        password = data['password']
        if len(username) and username.casefold() in password.casefold():
            raise serializers.ValidationError(
                _('The password is too similar to the username.'))
        return data

    def get_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class ChangePasswordSerializer(serializers.Serializer):
    '''Serializer for password change endpoint.'''
    current_password = serializers.CharField(
        max_length=150, write_only=True, required=True)
    new_password = serializers.CharField(
        max_length=150, write_only=True, required=True)

    def validate(self, attrs):
        self.validate_old_password(attrs)
        return super().validate(attrs)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value['current_password']):
            raise serializers.ValidationError(
                _('Your old password was entered incorrectly.'
                  'Please enter it again.')
            )
