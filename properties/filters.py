import django_filters
from django import forms
from .models import Property, PropertyType


class PropertyFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Keyword')
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains', label='City')
    property_type = django_filters.ModelChoiceFilter(queryset=PropertyType.objects.all(), label='Type', empty_label='All Types')
    status = django_filters.ChoiceFilter(choices=[('', 'All')] + Property.STATUS_CHOICES, label='Status')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Min Price')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Max Price')
    bedrooms = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='gte', label='Bedrooms')
    bathrooms = django_filters.NumberFilter(field_name='bathrooms', lookup_expr='gte', label='Bathrooms')
    min_area = django_filters.NumberFilter(field_name='area', lookup_expr='gte', label='Min Area')
    max_area = django_filters.NumberFilter(field_name='area', lookup_expr='lte', label='Max Area')

    class Meta:
        model = Property
        fields = ['keyword', 'city', 'property_type', 'status', 'min_price', 'max_price', 'bedrooms', 'bathrooms']
