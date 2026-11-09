from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_verified', 'date_joined']
    list_filter = ['role', 'is_verified', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('role', 'phone', 'avatar', 'bio', 'address', 'city', 'country', 'is_verified')}),
        ('Social', {'fields': ('website', 'facebook', 'twitter', 'instagram', 'linkedin', 'whatsapp')}),
    )
