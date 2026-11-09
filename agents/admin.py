from django.contrib import admin
from .models import AgentReview, Agency


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'email', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'city']
    search_fields = ['name', 'city']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_verified']


admin.site.register(AgentReview)
