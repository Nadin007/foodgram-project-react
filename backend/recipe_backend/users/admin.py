from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = [
        'avatar_tag',
        'username',
        'first_name',
        'last_name',
        'email',
        'role',
        'is_active',
        'bio',
    ]
    list_editable = ('role', )
    fieldsets = (
        (
            None,
            {'fields': (
                'username', 'email', 'password', 'role', 'bio', 'avatar')}
        ),
        ('Permissions',
         {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (
            None,
            {'classes': ('wide',),
             'fields': (
                'username',
                'first_name',
                'last_name',
                'email',
                'password1',
                'password2',
                'is_staff',
                'is_active',
                'role',
                'bio',)
             }
        ),
    )
    ordering = ('email', )
    search_fields = ('username', 'role')
    list_filter = ('is_active', 'role')
