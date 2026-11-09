from django.urls import path
from . import views

app_name = 'platform'

urlpatterns = [
    path('', views.admin_overview, name='overview'),
    path('listings/', views.admin_listings, name='listings'),
    path('listings/<int:pk>/approve/', views.admin_approve_listing, name='approve_listing'),
    path('listings/<int:pk>/reject/', views.admin_reject_listing, name='reject_listing'),
    path('verifications/', views.admin_verifications, name='verifications'),
    path('verifications/<int:pk>/approve/', views.admin_approve_verification, name='approve_verification'),
    path('verifications/<int:pk>/reject/', views.admin_reject_verification, name='reject_verification'),
    path('payments/', views.admin_payments, name='payments'),
    path('payments/<int:pk>/status/', views.admin_update_payment_status, name='payment_status'),
    path('agents/', views.admin_agents, name='agents'),
    path('buyers/', views.admin_buyers, name='buyers'),
    path('users/<int:pk>/edit/', views.admin_edit_user, name='edit_user'),
    path('users/<int:pk>/delete/', views.admin_delete_user, name='delete_user'),
    path('users/<int:pk>/hold/', views.admin_toggle_hold, name='toggle_hold'),
    path('reports/', views.admin_reports, name='reports'),
    path('reports/<int:pk>/resolve/', views.admin_resolve_report, name='resolve_report'),
]
