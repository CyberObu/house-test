import json
import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Case, When, IntegerField, Exists, OuterRef
from django.core.mail import send_mail
from django.conf import settings as django_settings
from .models import Property, PropertyType, Favorite, PropertyInquiry, Review, TourRequest, SavedSearch, PropertyReport, PropertyDocument
from .filters import PropertyFilter
from .forms import InquiryForm, ReviewForm, TourRequestForm, SavedSearchForm, PropertyReportForm
from dashboard.models import Payment

COMPARE_SESSION_KEY = 'compare_list'
MAX_COMPARE = 4


def property_list(request):
    qs = Property.objects.filter(is_published=True).select_related('property_type').prefetch_related('images')
    f = PropertyFilter(request.GET, queryset=qs)
    property_types = PropertyType.objects.all()
    cities = Property.objects.filter(is_published=True).values_list('city', flat=True).distinct()

    premium_ids  = Payment.objects.filter(plan='premium',  status='completed', user=OuterRef('owner')).values('id')[:1]
    standard_ids = Payment.objects.filter(plan='standard', status='completed', user=OuterRef('owner')).values('id')[:1]

    f_qs = f.qs.annotate(
        plan_priority=Case(
            When(Exists(premium_ids),  then=0),
            When(Exists(standard_ids), then=1),
            default=2,
            output_field=IntegerField(),
        )
    ).order_by('plan_priority', '-created_at')

    paginator = Paginator(f_qs, 9)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'properties/list.html', {
        'page_obj': page,
        'filter': f,
        'property_types': property_types,
        'cities': cities,
        'total': f.qs.count(),
        'compare_list': request.session.get(COMPARE_SESSION_KEY, []),
    })


def property_detail(request, slug):
    property = get_object_or_404(Property, slug=slug, is_published=True)
    property.views_count += 1
    property.save(update_fields=['views_count'])

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, property=property).exists()

    inquiry_form = InquiryForm(initial={
        'name': request.user.get_full_name() if request.user.is_authenticated else '',
        'email': request.user.email if request.user.is_authenticated else '',
    })
    review_form = ReviewForm()
    tour_form = TourRequestForm(initial={
        'name': request.user.get_full_name() if request.user.is_authenticated else '',
        'email': request.user.email if request.user.is_authenticated else '',
    })

    if request.method == 'POST':
        if 'inquiry_submit' in request.POST:
            inquiry_form = InquiryForm(request.POST)
            if inquiry_form.is_valid():
                inquiry = inquiry_form.save(commit=False)
                inquiry.property = property
                if request.user.is_authenticated:
                    inquiry.sender = request.user
                inquiry.save()
                _notify_inquiry(inquiry, property)
                messages.success(request, 'Your inquiry has been sent successfully!')
                return redirect('properties:detail', slug=slug)

        elif 'review_submit' in request.POST and request.user.is_authenticated:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.property = property
                review.reviewer = request.user
                review.save()
                messages.success(request, 'Your review has been submitted!')
                return redirect('properties:detail', slug=slug)

        elif 'tour_submit' in request.POST:
            tour_form = TourRequestForm(request.POST)
            if tour_form.is_valid():
                tour = tour_form.save(commit=False)
                tour.property = property
                if request.user.is_authenticated:
                    tour.requester = request.user
                tour.save()
                _notify_tour(tour, property)
                messages.success(request, 'Tour request submitted! The agent will confirm shortly.')
                return redirect('properties:detail', slug=slug)

    compare_list = request.session.get(COMPARE_SESSION_KEY, [])
    similar = Property.objects.filter(
        property_type=property.property_type, is_published=True
    ).exclude(pk=property.pk)[:3]

    video_embed = _get_embed_url(property.video_url) if property.video_url else None
    images_3d = property.images.filter(image_type='3d')
    report_form = PropertyReportForm(initial={
        'name': request.user.get_full_name() if request.user.is_authenticated else '',
        'email': request.user.email if request.user.is_authenticated else '',
    })

    if request.method == 'POST' and 'report_submit' in request.POST:
        report_form = PropertyReportForm(request.POST)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.property = property
            if request.user.is_authenticated:
                report.reporter = request.user
            report.save()
            messages.success(request, 'Report submitted. Thank you!')
            return redirect('properties:detail', slug=slug)

    return render(request, 'properties/detail.html', {
        'property': property,
        'is_favorited': is_favorited,
        'inquiry_form': inquiry_form,
        'review_form': review_form,
        'tour_form': tour_form,
        'report_form': report_form,
        'similar': similar,
        'compare_list': compare_list,
        'in_compare': property.pk in compare_list,
        'video_embed': video_embed,
        'images_3d': images_3d,
    })


def _get_embed_url(url):
    if not url:
        return None
    yt = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})', url)
    if yt:
        return f'https://www.youtube.com/embed/{yt.group(1)}'
    vm = re.search(r'vimeo\.com/(\d+)', url)
    if vm:
        return f'https://player.vimeo.com/video/{vm.group(1)}'
    return None


def _notify_inquiry(inquiry, property):
    owner_email = property.owner.email
    if not owner_email:
        return
    try:
        send_mail(
            subject=f'New Inquiry: {property.title}',
            message=(
                f'You have a new inquiry for "{property.title}".\n\n'
                f'From: {inquiry.name}\n'
                f'Email: {inquiry.email}\n'
                f'Phone: {inquiry.phone or "N/A"}\n\n'
                f'Message:\n{inquiry.message}\n\n'
                f'View property: {django_settings.SITE_URL if hasattr(django_settings, "SITE_URL") else ""}/properties/{property.slug}/'
            ),
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner_email],
            fail_silently=True,
        )
    except Exception:
        pass


def _notify_tour(tour, property):
    owner_email = property.owner.email
    if not owner_email:
        return
    try:
        send_mail(
            subject=f'Tour Request: {property.title}',
            message=(
                f'A tour has been requested for "{property.title}".\n\n'
                f'From: {tour.name}\n'
                f'Email: {tour.email}\n'
                f'Phone: {tour.phone or "N/A"}\n'
                f'Date: {tour.tour_date}\n'
                f'Time: {tour.tour_time}\n\n'
                f'Message:\n{tour.message or "None"}\n\n'
                f'Manage your tours in your dashboard.'
            ),
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner_email],
            fail_silently=True,
        )
    except Exception:
        pass


@login_required
def toggle_favorite(request, slug):
    property = get_object_or_404(Property, slug=slug)
    fav, created = Favorite.objects.get_or_create(user=request.user, property=property)
    if not created:
        fav.delete()
        saved = False
    else:
        saved = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'saved': saved})
    return redirect('properties:detail', slug=slug)


def property_type_list(request, slug):
    ptype = get_object_or_404(PropertyType, slug=slug)
    properties = Property.objects.filter(property_type=ptype, is_published=True).prefetch_related('images')
    paginator = Paginator(properties, 9)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'properties/list.html', {
        'page_obj': page,
        'property_type': ptype,
        'total': properties.count(),
        'filter': PropertyFilter(),
    })


# ── Compare ──────────────────────────────────────────────────────────────────

def compare_add(request, slug):
    property = get_object_or_404(Property, slug=slug, is_published=True)
    compare = request.session.get(COMPARE_SESSION_KEY, [])
    if property.pk not in compare:
        if len(compare) >= MAX_COMPARE:
            messages.warning(request, f'You can compare up to {MAX_COMPARE} properties at a time.')
        else:
            compare.append(property.pk)
            request.session[COMPARE_SESSION_KEY] = compare
            messages.success(request, f'"{property.title}" added to compare.')
    return redirect(request.META.get('HTTP_REFERER', 'properties:compare'))


def compare_remove(request, slug):
    property = get_object_or_404(Property, slug=slug)
    compare = request.session.get(COMPARE_SESSION_KEY, [])
    if property.pk in compare:
        compare.remove(property.pk)
        request.session[COMPARE_SESSION_KEY] = compare
    return redirect(request.META.get('HTTP_REFERER', 'properties:compare'))


def compare_clear(request):
    request.session[COMPARE_SESSION_KEY] = []
    return redirect('properties:compare')


def compare_view(request):
    compare_ids = request.session.get(COMPARE_SESSION_KEY, [])
    properties = list(Property.objects.filter(pk__in=compare_ids, is_published=True).prefetch_related('images', 'amenities'))
    all_amenities = set()
    for prop in properties:
        for a in prop.amenities.all():
            all_amenities.add(a.name)
    all_amenities = sorted(all_amenities)
    return render(request, 'properties/compare.html', {
        'properties': properties,
        'all_amenities': all_amenities,
    })


# ── Map Search ────────────────────────────────────────────────────────────────

def property_map(request):
    qs = Property.objects.filter(is_published=True, latitude__isnull=False, longitude__isnull=False)
    f = PropertyFilter(request.GET, queryset=qs)
    props_data = []
    for prop in f.qs.select_related('property_type').prefetch_related('images'):
        img = prop.get_main_image()
        props_data.append({
            'id': prop.pk,
            'title': prop.title,
            'slug': prop.slug,
            'price': str(prop.price),
            'status': prop.get_status_display(),
            'city': prop.city,
            'bedrooms': prop.bedrooms,
            'bathrooms': prop.bathrooms,
            'area': str(prop.area),
            'lat': float(prop.latitude),
            'lng': float(prop.longitude),
            'url': prop.get_absolute_url(),
            'image': img.image.url if img else '',
        })
    return render(request, 'properties/map.html', {
        'filter': PropertyFilter(request.GET),
        'props_json': json.dumps(props_data),
        'total': len(props_data),
    })


# ── Saved Searches ────────────────────────────────────────────────────────────

@login_required
def save_search(request):
    if request.method == 'POST':
        form = SavedSearchForm(request.POST)
        if form.is_valid():
            search = form.save(commit=False)
            search.user = request.user
            params = {k: v for k, v in request.POST.items()
                      if k not in ('csrfmiddlewaretoken', 'name', 'email_alerts', 'save_search_submit')}
            search.filters = params
            search.save()
            messages.success(request, f'Search "{search.name}" saved!')
        else:
            messages.error(request, 'Please provide a name for your saved search.')
    return redirect(request.META.get('HTTP_REFERER', 'properties:list'))


@login_required
def delete_saved_search(request, pk):
    search = get_object_or_404(SavedSearch, pk=pk, user=request.user)
    search.delete()
    messages.success(request, 'Saved search deleted.')
    return redirect('dashboard:saved_searches')


# ── Neighborhood Pages ────────────────────────────────────────────────────────

def neighborhood(request, city):
    properties = Property.objects.filter(city__iexact=city, is_published=True).prefetch_related('images')
    f = PropertyFilter(request.GET, queryset=properties)
    paginator = Paginator(f.qs, 9)
    page = paginator.get_page(request.GET.get('page'))
    stats = {
        'total': properties.count(),
        'for_sale': properties.filter(status='for_sale').count(),
        'for_rent': properties.filter(status='for_rent').count(),
    }
    cities = Property.objects.filter(is_published=True).values_list('city', flat=True).distinct()
    return render(request, 'properties/neighborhood.html', {
        'city': city,
        'page_obj': page,
        'filter': f,
        'stats': stats,
        'cities': cities,
    })


def all_neighborhoods(request):
    from django.db.models import Count
    cities = (Property.objects
              .filter(is_published=True)
              .values('city')
              .annotate(count=Count('id'))
              .order_by('-count'))
    return render(request, 'properties/neighborhoods.html', {'cities': cities})
