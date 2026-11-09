from django.shortcuts import render, redirect, get_object_or_404

PROPERTY_FORM_STEPS = [
    (1, 'Basic Info'),
    (2, 'Pricing & Details'),
    (3, 'Location'),
    (4, 'Nearby Places'),
    (5, 'Photos & Publish'),
]


def _save_floor_plans(request, prop):
    """Save floor plan images submitted as floorplan_image_N + floorplan_name_N."""
    files = request.FILES.getlist('floorplan_images')
    names = request.POST.getlist('floorplan_names')
    for i, img_file in enumerate(files):
        name = names[i].strip() if i < len(names) and names[i].strip() else f'Floor Plan {i + 1}'
        FloorPlan.objects.create(property=prop, name=name, image=img_file)


def _save_3d_images(request, prop):
    """Save 3D render images submitted as images_3d file input."""
    for img_file in request.FILES.getlist('images_3d'):
        PropertyImage.objects.create(property=prop, image=img_file, image_type='3d')


def _save_nearby_places(request, prop):
    """Parse nearby_name_N / nearby_type_N / nearby_distance_N from POST and save."""
    prop.nearby_places.all().delete()
    i = 0
    places = []
    while True:
        name = request.POST.get(f'nearby_name_{i}', '').strip()
        if not name:
            break
        places.append(NearbyPlace(
            property=prop,
            name=name,
            place_type=request.POST.get(f'nearby_type_{i}', 'other'),
            distance=request.POST.get(f'nearby_distance_{i}', '').strip(),
            order=i,
        ))
        i += 1
    if places:
        NearbyPlace.objects.bulk_create(places)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.utils import timezone
from functools import wraps
from django.http import HttpResponseForbidden
from properties.models import Property, PropertyImage, PropertyInquiry, Favorite, TourRequest, SavedSearch, NearbyPlace, FloorPlan
from properties.forms import PropertyForm
from accounts.forms import ProfileUpdateForm, ChangePasswordForm
from accounts.models import User, AgentVerification, UserReport
from django.contrib.auth import update_session_auth_hash
from .models import Payment
from .forms import PaymentForm


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return HttpResponseForbidden('<h1>403 – Admin access required</h1>')
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required
def dashboard_home(request):
    user = request.user

    if user.is_agent:
        my_properties = Property.objects.filter(owner=user).prefetch_related('images')
        inquiries_count = PropertyInquiry.objects.filter(property__owner=user, is_read=False).count()
        total_views = my_properties.aggregate(v=Sum('views_count'))['v'] or 0
        pending_tours = TourRequest.objects.filter(property__owner=user, status='pending').count()
        top_listings = my_properties.order_by('-views_count')[:5]
        chart_labels = [p.title[:20] for p in top_listings]
        chart_views = [p.views_count for p in top_listings]
        chart_inquiries = [PropertyInquiry.objects.filter(property=p).count() for p in top_listings]
        return render(request, 'dashboard/home.html', {
            'my_properties': my_properties[:5],
            'properties_count': my_properties.count(),
            'inquiries_count': inquiries_count,
            'total_views': total_views,
            'pending_tours': pending_tours,
            'top_listings': top_listings,
            'chart_labels': chart_labels,
            'chart_views': chart_views,
            'chart_inquiries': chart_inquiries,
        })
    else:
        # Buyer / Tenant
        my_favorites = Favorite.objects.filter(user=user).select_related('property').prefetch_related('property__images')
        my_saved_searches = SavedSearch.objects.filter(user=user)
        my_tours = TourRequest.objects.filter(requester=user).select_related('property').prefetch_related('property__images').order_by('-created_at')
        return render(request, 'dashboard/home.html', {
            'favorites_count': my_favorites.count(),
            'saved_searches_count': my_saved_searches.count(),
            'tours_count': my_tours.count(),
            'pending_tours_count': my_tours.filter(status='pending').count(),
            'my_favorites': my_favorites[:5],
            'my_tours': my_tours[:5],
        })


@login_required
def my_properties(request):
    props = Property.objects.filter(owner=request.user).prefetch_related('images')
    paginator = Paginator(props, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/my_properties.html', {'page_obj': page})


@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.is_published = False
            prop.approval_status = 'pending'
            prop.save()
            form.save_m2m()
            images = request.FILES.getlist('images')
            for i, img in enumerate(images):
                PropertyImage.objects.create(property=prop, image=img, is_main=(i == 0))
            _save_floor_plans(request, prop)
            _save_3d_images(request, prop)
            _save_nearby_places(request, prop)
            messages.success(request, 'Listing submitted for review! It will be published once approved by admin.')
            return redirect('dashboard:my_properties')
    else:
        form = PropertyForm()
    return render(request, 'dashboard/property_form.html', {
        'form': form, 'title': 'Add Property',
        'steps': PROPERTY_FORM_STEPS,
        'nearby_type_choices': NearbyPlace.TYPE_CHOICES,
    })


@login_required
def edit_property(request, slug):
    prop = get_object_or_404(Property, slug=slug, owner=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        if form.is_valid():
            form.save()
            images = request.FILES.getlist('images')
            for i, img in enumerate(images):
                PropertyImage.objects.create(property=prop, image=img)
            _save_floor_plans(request, prop)
            _save_3d_images(request, prop)
            _save_nearby_places(request, prop)
            messages.success(request, 'Property updated successfully!')
            return redirect('dashboard:my_properties')
    else:
        form = PropertyForm(instance=prop)
    return render(request, 'dashboard/property_form.html', {
        'form': form, 'title': 'Edit Property', 'prop': prop,
        'steps': PROPERTY_FORM_STEPS,
        'nearby_type_choices': NearbyPlace.TYPE_CHOICES,
        'existing_nearby': list(prop.nearby_places.values('name', 'place_type', 'distance')),
    })


@login_required
def delete_property(request, slug):
    prop = get_object_or_404(Property, slug=slug, owner=request.user)
    if request.method == 'POST':
        prop.delete()
        messages.success(request, 'Property deleted.')
    return redirect('dashboard:my_properties')


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('property').prefetch_related('property__images')
    return render(request, 'dashboard/my_favorites.html', {'favorites': favorites})


@login_required
def my_inquiries(request):
    inquiries = PropertyInquiry.objects.filter(property__owner=request.user).select_related('property')
    inquiries.filter(is_read=False).update(is_read=True)
    return render(request, 'dashboard/my_inquiries.html', {'inquiries': inquiries})


@login_required
def payments_view(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.amount = Payment.PLAN_PRICES.get(payment.plan, 0)
            payment.save()
            messages.success(request, f'Payment request submitted! Please pay {payment.amount:,} TZS to +255 XXX XXX XXX via {payment.payment_method}. Your listing will be activated within 1 hour.')
            return redirect('dashboard:payments')
    else:
        form = PaymentForm()
    payments = Payment.objects.filter(user=request.user)
    plans = [
        ('basic', 'Basic', Payment.PLAN_PRICES['basic'], ['1 Property Listing', 'Basic Support', '30 Days Active', 'Email Notifications']),
        ('standard', 'Standard', Payment.PLAN_PRICES['standard'], ['5 Property Listings', 'Priority Support', '90 Days Active', 'Email & SMS Alerts', 'Featured Badge']),
        ('premium', 'Premium', Payment.PLAN_PRICES['premium'], ['Unlimited Listings', 'Dedicated Support', 'Always Active', 'All Notifications', 'Top Placement', 'Analytics Dashboard']),
    ]
    return render(request, 'dashboard/payments.html', {'form': form, 'payments': payments, 'plans': plans})


@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('dashboard:profile_settings')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'dashboard/profile_settings.html', {'form': form})


@login_required
def my_tours(request):
    # Tours requested by user OR for properties owned by user
    as_requester = TourRequest.objects.filter(requester=request.user).select_related('property')
    as_owner = TourRequest.objects.filter(property__owner=request.user).select_related('property')
    return render(request, 'dashboard/my_tours.html', {
        'as_requester': as_requester,
        'as_owner': as_owner,
    })


@login_required
def update_tour_status(request, pk):
    tour = get_object_or_404(TourRequest, pk=pk, property__owner=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ('confirmed', 'cancelled'):
            tour.status = status
            tour.save()
            messages.success(request, f'Tour {status}.')
    return redirect('dashboard:my_tours')


@login_required
def saved_searches(request):
    searches = SavedSearch.objects.filter(user=request.user)
    return render(request, 'dashboard/saved_searches.html', {'searches': searches})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('dashboard:profile_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'dashboard/change_password.html', {'form': form})


# ── Admin Views ───────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_overview(request):
    pending_listings = Property.objects.filter(approval_status='pending').count()
    pending_verifs   = AgentVerification.objects.filter(status='pending').count()
    total_agents     = User.objects.filter(role='agent').count()
    total_listings   = Property.objects.count()
    total_buyers     = User.objects.filter(role='buyer').count()
    recent_listings  = Property.objects.filter(approval_status='pending').order_by('-created_at')[:5]
    recent_verifs    = AgentVerification.objects.filter(status='pending').order_by('-submitted_at')[:5]
    return render(request, 'dashboard/admin_overview.html', {
        'pending_listings': pending_listings,
        'pending_verifs': pending_verifs,
        'total_agents': total_agents,
        'total_listings': total_listings,
        'total_buyers': total_buyers,
        'recent_listings': recent_listings,
        'recent_verifs': recent_verifs,
    })


@login_required
@admin_required
def admin_listings(request):
    status_filter = request.GET.get('status', 'pending')
    listings = Property.objects.filter(approval_status=status_filter).select_related('owner').prefetch_related('images').order_by('-created_at')
    paginator = Paginator(listings, 15)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/admin_listings.html', {'page_obj': page, 'status_filter': status_filter})


@login_required
@admin_required
def admin_approve_listing(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        prop.approval_status = 'approved'
        prop.is_published = True
        prop.rejection_reason = ''
        prop.save(update_fields=['approval_status', 'is_published', 'rejection_reason'])
        messages.success(request, f'Listing "{prop.title}" approved and published.')
    return redirect('platform:listings')


@login_required
@admin_required
def admin_reject_listing(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        prop.approval_status = 'rejected'
        prop.is_published = False
        prop.rejection_reason = reason
        prop.save(update_fields=['approval_status', 'is_published', 'rejection_reason'])
        messages.success(request, f'Listing "{prop.title}" rejected.')
    return redirect('platform:listings')


@login_required
@admin_required
def admin_verifications(request):
    status_filter = request.GET.get('status', 'pending')
    verifs = AgentVerification.objects.filter(status=status_filter).select_related('user').order_by('-submitted_at')
    paginator = Paginator(verifs, 15)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/admin_verifications.html', {'page_obj': page, 'status_filter': status_filter})


@login_required
@admin_required
def admin_approve_verification(request, pk):
    verif = get_object_or_404(AgentVerification, pk=pk)
    if request.method == 'POST':
        verif.status = 'approved'
        verif.rejection_reason = ''
        verif.reviewed_at = timezone.now()
        verif.save(update_fields=['status', 'rejection_reason', 'reviewed_at'])
        verif.user.is_verified = True
        verif.user.save(update_fields=['is_verified'])
        messages.success(request, f'Agent {verif.user.get_full_name()} verified successfully.')
    return redirect('platform:verifications')


@login_required
@admin_required
def admin_reject_verification(request, pk):
    verif = get_object_or_404(AgentVerification, pk=pk)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        verif.status = 'rejected'
        verif.rejection_reason = reason
        verif.reviewed_at = timezone.now()
        verif.save(update_fields=['status', 'rejection_reason', 'reviewed_at'])
        verif.user.is_verified = False
        verif.user.save(update_fields=['is_verified'])
        messages.success(request, f'Agent {verif.user.get_full_name()} verification rejected.')
    return redirect('platform:verifications')


# ── Admin Payment Management ─────────────────────────────────────────────────

@login_required
@admin_required
def admin_payments(request):
    status_filter = request.GET.get('status', '')
    plan_filter = request.GET.get('plan', '')
    qs = Payment.objects.select_related('user').order_by('-created_at')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if plan_filter:
        qs = qs.filter(plan=plan_filter)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    totals = {
        'pending': Payment.objects.filter(status='pending').count(),
        'completed': Payment.objects.filter(status='completed').count(),
        'failed': Payment.objects.filter(status='failed').count(),
    }
    return render(request, 'dashboard/admin_payments.html', {
        'page_obj': page,
        'status_filter': status_filter,
        'plan_filter': plan_filter,
        'totals': totals,
    })


@login_required
@admin_required
def admin_update_payment_status(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ('pending', 'completed', 'failed'):
            payment.status = new_status
            transaction_id = request.POST.get('transaction_id', '').strip()
            if transaction_id:
                payment.transaction_id = transaction_id
            payment.save(update_fields=['status', 'transaction_id'])
            messages.success(request, f'Payment status updated to {new_status}.')
    return redirect('platform:payments')


# ── Admin: All Agents ────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_agents(request):
    search = request.GET.get('q', '').strip()
    verified_filter = request.GET.get('verified', '')
    qs = User.objects.filter(role='agent').select_related('agency').prefetch_related('payments').order_by('-date_joined')
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    if verified_filter == '1':
        qs = qs.filter(is_verified=True)
    elif verified_filter == '0':
        qs = qs.filter(is_verified=False)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/admin_agents.html', {
        'page_obj': page,
        'search': search,
        'verified_filter': verified_filter,
        'total': qs.count(),
    })


# ── Agent: Engaged Buyers ─────────────────────────────────────────────────────

@login_required
def my_buyers(request):
    if not request.user.is_agent:
        return redirect('dashboard:home')
    # Collect buyers/contacts from inquiries
    inquiries = (PropertyInquiry.objects
                 .filter(property__owner=request.user)
                 .select_related('property', 'sender')
                 .order_by('-created_at'))
    # Collect from tour requests
    tours = (TourRequest.objects
             .filter(property__owner=request.user)
             .select_related('property', 'requester')
             .order_by('-created_at'))

    # Build a unified list keyed by email to avoid duplicates
    buyers_map = {}
    for inq in inquiries:
        key = inq.email.lower()
        if key not in buyers_map:
            buyers_map[key] = {
                'name': inq.name,
                'email': inq.email,
                'phone': inq.phone,
                'user': inq.sender,
                'inquiries': [],
                'tours': [],
                'last_contact': inq.created_at,
            }
        buyers_map[key]['inquiries'].append(inq)
        if inq.created_at > buyers_map[key]['last_contact']:
            buyers_map[key]['last_contact'] = inq.created_at

    for tour in tours:
        key = tour.email.lower()
        if key not in buyers_map:
            buyers_map[key] = {
                'name': tour.name,
                'email': tour.email,
                'phone': tour.phone,
                'user': tour.requester,
                'inquiries': [],
                'tours': [],
                'last_contact': tour.created_at,
            }
        buyers_map[key]['tours'].append(tour)
        if tour.created_at > buyers_map[key]['last_contact']:
            buyers_map[key]['last_contact'] = tour.created_at

    buyers = sorted(buyers_map.values(), key=lambda x: x['last_contact'], reverse=True)
    return render(request, 'dashboard/my_buyers.html', {'buyers': buyers})


# ── Buyer: Agents I've Engaged With ──────────────────────────────────────────

@login_required
def my_agents(request):
    # Inquiries sent by this buyer
    inquiries = (PropertyInquiry.objects
                 .filter(sender=request.user)
                 .select_related('property', 'property__owner')
                 .order_by('-created_at'))
    # Tour requests made by this buyer
    tours = (TourRequest.objects
             .filter(requester=request.user)
             .select_related('property', 'property__owner')
             .order_by('-created_at'))

    agents_map = {}
    for inq in inquiries:
        owner = inq.property.owner
        if owner.pk not in agents_map:
            agents_map[owner.pk] = {
                'agent': owner,
                'inquiries': [],
                'tours': [],
                'last_contact': inq.created_at,
            }
        agents_map[owner.pk]['inquiries'].append(inq)
        if inq.created_at > agents_map[owner.pk]['last_contact']:
            agents_map[owner.pk]['last_contact'] = inq.created_at

    for tour in tours:
        owner = tour.property.owner
        if owner.pk not in agents_map:
            agents_map[owner.pk] = {
                'agent': owner,
                'inquiries': [],
                'tours': [],
                'last_contact': tour.created_at,
            }
        agents_map[owner.pk]['tours'].append(tour)
        if tour.created_at > agents_map[owner.pk]['last_contact']:
            agents_map[owner.pk]['last_contact'] = tour.created_at

    agents = sorted(agents_map.values(), key=lambda x: x['last_contact'], reverse=True)
    return render(request, 'dashboard/my_agents.html', {'agents': agents})


# ── Admin: All Buyers/Tenants ─────────────────────────────────────────────────

@login_required
@admin_required
def admin_buyers(request):
    search = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    qs = User.objects.filter(role='buyer').order_by('-date_joined')
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    if status_filter == 'active':
        qs = qs.filter(is_active=True)
    elif status_filter == 'held':
        qs = qs.filter(is_active=False)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/admin_buyers.html', {
        'page_obj': page,
        'search': search,
        'status_filter': status_filter,
        'total': qs.count(),
    })


# ── Admin: Edit User ──────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_edit_user(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_obj.first_name  = request.POST.get('first_name', user_obj.first_name).strip()
        user_obj.last_name   = request.POST.get('last_name',  user_obj.last_name).strip()
        user_obj.email       = request.POST.get('email',      user_obj.email).strip()
        user_obj.phone       = request.POST.get('phone',      user_obj.phone).strip()
        user_obj.city        = request.POST.get('city',       user_obj.city).strip()
        new_role = request.POST.get('role', user_obj.role)
        if new_role in ('buyer', 'agent', 'admin'):
            user_obj.role = new_role
        user_obj.is_verified = request.POST.get('is_verified') == 'on'
        user_obj.save()
        messages.success(request, f'User {user_obj.get_full_name()} updated.')
        back = 'platform:agents' if user_obj.role == 'agent' else 'platform:buyers'
        return redirect(back)
    return render(request, 'dashboard/admin_edit_user.html', {'user_obj': user_obj})


# ── Admin: Delete User ────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_delete_user(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        role = user_obj.role
        name = user_obj.get_full_name() or user_obj.email
        user_obj.delete()
        messages.success(request, f'User "{name}" deleted.')
        return redirect('platform:agents' if role == 'agent' else 'platform:buyers')
    return redirect('platform:overview')


# ── Admin: Hold / Unhold User ─────────────────────────────────────────────────

@login_required
@admin_required
def admin_toggle_hold(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_obj.is_active = not user_obj.is_active
        user_obj.save(update_fields=['is_active'])
        state = 'reactivated' if user_obj.is_active else 'suspended'
        messages.success(request, f'Account {state} for {user_obj.get_full_name() or user_obj.email}.')
    return redirect(request.META.get('HTTP_REFERER', 'platform:overview'))


# ── Admin: Reports Inbox ──────────────────────────────────────────────────────

@login_required
@admin_required
def admin_reports(request):
    status_filter = request.GET.get('status', 'open')
    qs = UserReport.objects.select_related('reporter', 'reported_user').order_by('-created_at')
    if status_filter == 'open':
        qs = qs.filter(is_resolved=False)
    elif status_filter == 'resolved':
        qs = qs.filter(is_resolved=True)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/admin_reports.html', {
        'page_obj': page,
        'status_filter': status_filter,
        'open_count': UserReport.objects.filter(is_resolved=False).count(),
    })


@login_required
@admin_required
def admin_resolve_report(request, pk):
    report = get_object_or_404(UserReport, pk=pk)
    if request.method == 'POST':
        report.admin_notes = request.POST.get('admin_notes', '').strip()
        report.is_resolved = True
        report.save(update_fields=['is_resolved', 'admin_notes'])
        messages.success(request, 'Report marked as resolved.')
    return redirect('platform:reports')


# ── Users: Submit Secret Report ───────────────────────────────────────────────

@login_required
def report_user(request, pk):
    reported = get_object_or_404(User, pk=pk)
    if reported == request.user:
        messages.error(request, 'You cannot report yourself.')
        return redirect('dashboard:home')
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        description = request.POST.get('description', '').strip()
        if reason and description:
            UserReport.objects.create(
                reporter=request.user,
                reported_user=reported,
                reason=reason,
                description=description,
            )
            messages.success(request, 'Your report has been submitted confidentially to the admin team.')
        else:
            messages.error(request, 'Please select a reason and provide a description.')
        return redirect(request.POST.get('next', 'dashboard:home'))
    return render(request, 'dashboard/report_user.html', {
        'reported': reported,
        'reason_choices': UserReport.REASON_CHOICES,
        'next': request.META.get('HTTP_REFERER', '/dashboard/'),
    })


# ── Agent Verification View ───────────────────────────────────────────────────

@login_required
def agent_verification(request):
    if not request.user.is_agent:
        return redirect('dashboard:home')
    verif = None
    try:
        verif = request.user.verification
    except AgentVerification.DoesNotExist:
        pass

    if request.method == 'POST' and (verif is None or verif.status == 'rejected'):
        if verif and verif.status == 'rejected':
            verif.delete()
        verif = AgentVerification(user=request.user)
        verif.full_name      = request.POST.get('full_name', '')
        verif.date_of_birth  = request.POST.get('date_of_birth')
        verif.nationality    = request.POST.get('nationality', 'Tanzanian')
        verif.address        = request.POST.get('address', '')
        verif.nida_number    = request.POST.get('nida_number', '')
        verif.license_number = request.POST.get('license_number', '')
        if 'nida_document' in request.FILES:
            verif.nida_document = request.FILES['nida_document']
        if 'birth_certificate' in request.FILES:
            verif.birth_certificate = request.FILES['birth_certificate']
        if 'passport_photo' in request.FILES:
            verif.passport_photo = request.FILES['passport_photo']
        if 'license_document' in request.FILES:
            verif.license_document = request.FILES['license_document']
        verif.status = 'pending'
        verif.save()
        messages.success(request, 'Verification application submitted! We will review your documents within 2-3 business days.')
        return redirect('dashboard:agent_verification')

    return render(request, 'dashboard/agent_verification.html', {'verif': verif})
