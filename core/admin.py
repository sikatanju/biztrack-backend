from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

from .models import User
# Register your models here.
@admin.register(User) 
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )