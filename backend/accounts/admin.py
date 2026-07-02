from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'loyalty_points', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Customer Info', {'fields': ('phone', 'address', 'is_subscribed_newsletter', 'loyalty_points')}),
    )
