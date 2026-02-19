from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "email", "username", "is_staff")
    ordering = ("email",)
    fieldsets = UserAdmin.fieldsets + (("Profile", {"fields": ()}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("email",)}),)
