from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from accounts.models import User
from properties.models import Property
from .models import Agency


def agent_list(request):
    agents = User.objects.filter(role='agent').select_related('agency').prefetch_related('properties')
    city = request.GET.get('city', '')
    if city:
        agents = agents.filter(city__icontains=city)
    paginator = Paginator(agents, 9)
    page = paginator.get_page(request.GET.get('page'))
    agencies = Agency.objects.all()[:6]
    return render(request, 'agents/list.html', {'page_obj': page, 'agencies': agencies})


def agent_detail(request, pk):
    agent = get_object_or_404(User, pk=pk, role='agent')
    properties = Property.objects.filter(owner=agent, is_published=True).prefetch_related('images')
    paginator = Paginator(properties, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'agents/detail.html', {'agent': agent, 'page_obj': page})


def agency_list(request):
    agencies = Agency.objects.all()
    paginator = Paginator(agencies, 9)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'agents/agency_list.html', {'page_obj': page})


def agency_detail(request, slug):
    agency = get_object_or_404(Agency, slug=slug)
    agents = agency.members.filter(role='agent')
    properties = Property.objects.filter(owner__agency=agency, is_published=True).prefetch_related('images')
    paginator = Paginator(properties, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'agents/agency_detail.html', {
        'agency': agency,
        'agents': agents,
        'page_obj': page,
    })
