from django import forms
from .models import Property, PropertyImage, PropertyInquiry, Review, FloorPlan, TourRequest, SavedSearch, PropertyReport


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'status', 'label',
            'price', 'price_postfix', 'bedrooms', 'bathrooms', 'garages',
            'area', 'year_built', 'address', 'city', 'state', 'zip_code',
            'country', 'latitude', 'longitude', 'amenities', 'tags',
            'video_url', 'virtual_tour_url', 'is_featured', 'is_published',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'amenities': forms.CheckboxSelectMultiple(),
            'video_url': forms.URLInput(attrs={'placeholder': 'https://www.youtube.com/watch?v=...'}),
        }


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_main']


class InquiryForm(forms.ModelForm):
    class Meta:
        model = PropertyInquiry
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'I am interested in this property...'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.RadioSelect(),
        }


class TourRequestForm(forms.ModelForm):
    class Meta:
        model = TourRequest
        fields = ['name', 'email', 'phone', 'tour_date', 'tour_time', 'message']
        widgets = {
            'tour_date': forms.DateInput(attrs={'type': 'date'}),
            'tour_time': forms.TimeInput(attrs={'type': 'time'}),
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special requests or questions...'}),
        }


class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedSearch
        fields = ['name', 'email_alerts']


class PropertyReportForm(forms.ModelForm):
    class Meta:
        model = PropertyReport
        fields = ['name', 'email', 'reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Please provide details...'}),
        }
