from django.shortcuts import render, redirect
from django.contrib import messages
from properties.models import Property, PropertyType
from agents.models import AgentReview
from accounts.models import User
from blog.models import Post
from .models import Testimonial
from .forms import ContactForm


def home(request):
    featured = Property.objects.filter(is_published=True, is_featured=True).prefetch_related('images')[:6]
    recent = Property.objects.filter(is_published=True).prefetch_related('images')[:8]
    for_sale = Property.objects.filter(is_published=True, status='for_sale').prefetch_related('images')[:4]
    for_rent = Property.objects.filter(is_published=True, status='for_rent').prefetch_related('images')[:4]
    property_types = PropertyType.objects.all()
    agents = User.objects.filter(role='agent')[:4]
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    blog_posts = Post.objects.filter(is_published=True)[:3]
    stats = {
        'properties': Property.objects.filter(is_published=True).count(),
        'agents': User.objects.filter(role='agent').count(),
        'cities': Property.objects.filter(is_published=True).values('city').distinct().count(),
        'sold': Property.objects.filter(status__in=['sold', 'rented']).count(),
    }
    return render(request, 'core/home.html', {
        'featured': featured,
        'recent': recent,
        'for_sale': for_sale,
        'for_rent': for_rent,
        'property_types': property_types,
        'agents': agents,
        'testimonials': testimonials,
        'blog_posts': blog_posts,
        'stats': stats,
    })


def about(request):
    agents = User.objects.filter(role='agent')[:8]
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    return render(request, 'core/about.html', {'agents': agents, 'testimonials': testimonials})


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms_conditions(request):
    return render(request, 'core/terms_conditions.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('core:contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})
