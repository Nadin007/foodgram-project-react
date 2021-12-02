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
    ]
    list_editable = ('role', )
    fieldsets = (
        (
            None,
            {'fields': (
                'username', 'email', 'password', 'role', 'avatar')}
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
                'role')
             }
        ),
    )
    ordering = ('email', )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
