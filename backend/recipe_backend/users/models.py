import os

from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.safestring import mark_safe

from recipe_backend.settings import BASE_DIR


class ROLE_CHOICES(models.TextChoices):
    USER = 'user'
    ADMIN = 'admin'


class User(AbstractUser):
    '''Model for user.'''
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        verbose_name='username', max_length=150,
        unique=True, help_text='Please enter up to 150 characters',
        validators=[username_validator],
        error_messages={
            'unique': 'User with the same username already exists'})
    first_name = models.CharField(
        verbose_name='first name', max_length=150, blank=True)
    last_name = models.CharField(
        verbose_name='last name', max_length=150, blank=True)
    email = models.EmailField(
        verbose_name='email address', blank=False,
        unique=True, max_length=254)
    role = models.CharField(
        verbose_name='user`s role', choices=ROLE_CHOICES.choices,
        default=ROLE_CHOICES.USER, null=False,
        max_length=60)
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name='avatar', help_text='Choose the avatar',
        blank=True, null=False, default='avatars/default-1.png')
    date_joined = models.DateTimeField(
        verbose_name='date joined', default=timezone.now)
    password = models.CharField(verbose_name='password', max_length=150)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        constraints = [
            models.CheckConstraint(
                check=~Q(username='me'),
                name='User can be called \'me\'!'
            )
        ]

    def __str__(self) -> str:
        return f'{self.username} is a {self.role}'

    def save(self, *args, **kwargs) -> None:
        if self.is_superuser:
            self.role = ROLE_CHOICES.ADMIN
            self.is_active = True
        return super().save()

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        return os.path.join(BASE_DIR, 'media/avatars/default-1.png')

    def avatar_tag(self):
        return mark_safe(
            '<img src="%s" width="50" height="50" />' % self.get_avatar())
    avatar_tag.short_description = 'avatar'
