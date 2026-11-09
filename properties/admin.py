from django.contrib import admin
from .models import (Property, PropertyImage, PropertyType, Amenity, FloorPlan,
                     PropertyInquiry, Favorite, Review, TourRequest, SavedSearch,
                     OpenHouse, PropertyDocument, PropertyReport)


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3


class FloorPlanInline(admin.TabularInline):
    model = FloorPlan
    extra = 1


class OpenHouseInline(admin.TabularInline):
    model = OpenHouse
    extra = 1


class PropertyDocumentInline(admin.TabularInline):
    model = PropertyDocument
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'status', 'price', 'city', 'is_featured', 'is_published', 'created_at']
    list_filter = ['status', 'property_type', 'is_featured', 'is_published', 'city']
    search_fields = ['title', 'address', 'city']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PropertyImageInline, FloorPlanInline, OpenHouseInline, PropertyDocumentInline]
    list_editable = ['is_featured', 'is_published']


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    pass


@admin.register(PropertyInquiry)
class PropertyInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'property', 'is_read', 'created_at']
    list_filter = ['is_read']


admin.site.register(Favorite)
admin.site.register(Review)


@admin.register(TourRequest)
class TourRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'property', 'tour_date', 'tour_time', 'status', 'created_at']
    list_filter = ['status', 'tour_date']
    list_editable = ['status']


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'email_alerts', 'created_at']


@admin.register(PropertyReport)
class PropertyReportAdmin(admin.ModelAdmin):
    list_display = ['property', 'reason', 'name', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved']
    list_editable = ['is_resolved']


admin.site.register(OpenHouse)
admin.site.register(PropertyDocument)
