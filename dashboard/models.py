from django.db import models
from django.conf import settings


class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    PLAN_BASIC = 'basic'
    PLAN_STANDARD = 'standard'
    PLAN_PREMIUM = 'premium'
    PLAN_CHOICES = [
        (PLAN_BASIC, 'Basic - 1 Listing'),
        (PLAN_STANDARD, 'Standard - 5 Listings'),
        (PLAN_PREMIUM, 'Premium - Unlimited'),
    ]

    PLAN_PRICES = {
        PLAN_BASIC: 10000,
        PLAN_STANDARD: 35000,
        PLAN_PREMIUM: 80000,
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, help_text='e.g. M-Pesa, Tigo Pesa, Airtel Money')
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.plan} ({self.status})'
