from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from taggit.managers import TaggableManager


class PropertyType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='fas fa-home')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fas fa-check')

    class Meta:
        verbose_name_plural = 'Amenities'

    def __str__(self):
        return self.name


class Property(models.Model):
    STATUS_FOR_SALE = 'for_sale'
    STATUS_FOR_RENT = 'for_rent'
    STATUS_SOLD = 'sold'
    STATUS_RENTED = 'rented'
    STATUS_CHOICES = [
        (STATUS_FOR_SALE, 'For Sale'),
        (STATUS_FOR_RENT, 'For Rent'),
        (STATUS_SOLD, 'Sold'),
        (STATUS_RENTED, 'Rented'),
    ]

    LABEL_FEATURED = 'featured'
    LABEL_HOT = 'hot'
    LABEL_NEW = 'new'
    LABEL_OPEN_HOUSE = 'open_house'
    LABEL_CHOICES = [
        (LABEL_FEATURED, 'Featured'),
        (LABEL_HOT, 'Hot Offer'),
        (LABEL_NEW, 'New'),
        (LABEL_OPEN_HOUSE, 'Open House'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True, related_name='properties')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_FOR_SALE)
    label = models.CharField(max_length=20, choices=LABEL_CHOICES, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    price_postfix = models.CharField(max_length=20, blank=True, help_text='e.g. /month, /year')

    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    garages = models.PositiveSmallIntegerField(default=0)
    area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Area in sq ft')
    year_built = models.PositiveIntegerField(blank=True, null=True)

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Tanzania')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    amenities = models.ManyToManyField(Amenity, blank=True)
    tags = TaggableManager(blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    approval_status = models.CharField(max_length=20, choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    rejection_reason = models.TextField(blank=True)
    views_count = models.PositiveIntegerField(default=0)

    video_url = models.URLField(blank=True, help_text='YouTube or Vimeo URL')
    virtual_tour_url = models.URLField(blank=True, help_text='Matterport or other 3D virtual tour embed URL')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Property.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('properties:detail', kwargs={'slug': self.slug})

    def get_main_image(self):
        img = self.images.filter(is_main=True).first()
        return img or self.images.first()

    @property
    def status_badge_color(self):
        colors = {
            'for_sale': 'bg-blue-500',
            'for_rent': 'bg-green-500',
            'sold': 'bg-red-500',
            'rented': 'bg-orange-500',
        }
        return colors.get(self.status, 'bg-gray-500')


class PropertyImage(models.Model):
    TYPE_PHOTO = 'photo'
    TYPE_3D = '3d'
    TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('3d',    '3D Render / 360°'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    caption = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    image_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='photo')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'Image for {self.property.title}'


class NearbyPlace(models.Model):
    TYPE_CHOICES = [
        ('hospital',    'Hospital'),
        ('clinic',      'Clinic / Health Centre'),
        ('school',      'School'),
        ('university',  'University / College'),
        ('restaurant',  'Restaurant / Café'),
        ('supermarket', 'Supermarket / Market'),
        ('bank',        'Bank / ATM'),
        ('pharmacy',    'Pharmacy'),
        ('park',        'Park / Garden'),
        ('gym',         'Gym / Sports Centre'),
        ('mosque',      'Mosque'),
        ('church',      'Church'),
        ('bus_stop',    'Bus Stop'),
        ('airport',     'Airport'),
        ('mall',        'Shopping Mall'),
        ('other',       'Other'),
    ]
    TYPE_ICONS = {
        'hospital': 'fas fa-hospital',
        'clinic': 'fas fa-stethoscope',
        'school': 'fas fa-school',
        'university': 'fas fa-graduation-cap',
        'restaurant': 'fas fa-utensils',
        'supermarket': 'fas fa-shopping-cart',
        'bank': 'fas fa-university',
        'pharmacy': 'fas fa-pills',
        'park': 'fas fa-tree',
        'gym': 'fas fa-dumbbell',
        'mosque': 'fas fa-mosque',
        'church': 'fas fa-church',
        'bus_stop': 'fas fa-bus',
        'airport': 'fas fa-plane',
        'mall': 'fas fa-store',
        'other': 'fas fa-map-pin',
    }

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='nearby_places')
    name = models.CharField(max_length=200)
    place_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    distance = models.CharField(max_length=50, blank=True, help_text='e.g. 500m, 2km')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.name} – {self.get_place_type_display()}'

    def get_icon(self):
        return self.TYPE_ICONS.get(self.place_type, 'fas fa-map-pin')


class FloorPlan(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='floor_plans')
    name = models.CharField(max_length=100)
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='floorplans/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.name} - {self.property.title}'


class PropertyInquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Property Inquiries'

    def __str__(self):
        return f'Inquiry from {self.name} for {self.property.title}'


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'property']

    def __str__(self):
        return f'{self.user} saved {self.property.title}'


class Review(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['property', 'reviewer']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.rating}★ review by {self.reviewer} on {self.property.title}'


class TourRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='tour_requests')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    tour_date = models.DateField()
    tour_time = models.TimeField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Tour by {self.name} for {self.property.title} on {self.tour_date}'


class OpenHouse(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='open_houses')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f'Open House: {self.property.title} on {self.date}'


class PropertyDocument(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='property_docs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} – {self.property.title}'


class PropertyReport(models.Model):
    REASON_CHOICES = [
        ('wrong_info', 'Wrong Information'),
        ('duplicate', 'Duplicate Listing'),
        ('fraud', 'Suspected Fraud'),
        ('already_sold', 'Already Sold/Rented'),
        ('other', 'Other'),
    ]
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f'Report: {self.property.title} – {self.get_reason_display()}'


class SavedSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100)
    filters = models.JSONField(default=dict)
    email_alerts = models.BooleanField(default=True)
    last_notified = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} by {self.user}'

    def get_results_url(self):
        from django.http import QueryDict
        qd = QueryDict(mutable=True)
        qd.update(self.filters)
        return f'/properties/?{qd.urlencode()}'
