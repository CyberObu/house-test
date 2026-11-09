from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'plan', 'payment_method']
    search_fields = ['user__email', 'transaction_id']
