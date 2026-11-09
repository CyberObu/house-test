from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    ROLE_BUYER = 'buyer'
    ROLE_AGENT = 'agent'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_BUYER, 'Buyer'),
        (ROLE_AGENT, 'Agent'),
        (ROLE_ADMIN, 'Admin'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_BUYER)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    agency = models.ForeignKey('agents.Agency', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username or self.get_full_name() or self.email

    @property
    def is_agent(self):
        return self.role == self.ROLE_AGENT

    @property
    def is_buyer(self):
        return self.role == self.ROLE_BUYER

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.svg'


class UserReport(models.Model):
    REASON_CHOICES = [
        ('misconduct',        'Misconduct / Bad Behaviour'),
        ('fraud',             'Fraud / Scam'),
        ('breach_of_contract','Breach of Contract'),
        ('harassment',        'Harassment'),
        ('security_breach',   'Security / Privacy Breach'),
        ('fake_listing',      'Fake or Misleading Listing'),
        ('other',             'Other'),
    ]
    reporter      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_received')
    reason        = models.CharField(max_length=30, choices=REASON_CHOICES)
    description   = models.TextField()
    is_resolved   = models.BooleanField(default=False)
    admin_notes   = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Report by {self.reporter} against {self.reported_user} ({self.reason})'


class AgentVerification(models.Model):
    STATUS_PENDING  = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES  = [('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')]

    user              = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification')
    full_name         = models.CharField(max_length=200)
    date_of_birth     = models.DateField()
    nationality       = models.CharField(max_length=100, default='Tanzanian')
    address           = models.TextField()
    nida_number       = models.CharField(max_length=50)
    nida_document     = models.FileField(upload_to='verifications/nida/')
    birth_certificate = models.FileField(upload_to='verifications/birth/', blank=True, null=True)
    passport_photo    = models.ImageField(upload_to='verifications/passport/')
    license_number    = models.CharField(max_length=100, blank=True)
    license_document  = models.FileField(upload_to='verifications/license/', blank=True, null=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason  = models.TextField(blank=True)
    submitted_at      = models.DateTimeField(auto_now_add=True)
    reviewed_at       = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} – {self.status}'
