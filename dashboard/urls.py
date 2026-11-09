from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('properties/', views.my_properties, name='my_properties'),
    path('properties/add/', views.add_property, name='add_property'),
    path('properties/<slug:slug>/edit/', views.edit_property, name='edit_property'),
    path('properties/<slug:slug>/delete/', views.delete_property, name='delete_property'),
    path('favorites/', views.my_favorites, name='my_favorites'),
    path('inquiries/', views.my_inquiries, name='my_inquiries'),
    path('tours/', views.my_tours, name='my_tours'),
    path('tours/<int:pk>/status/', views.update_tour_status, name='update_tour_status'),
    path('saved-searches/', views.saved_searches, name='saved_searches'),
    path('payments/', views.payments_view, name='payments'),
    path('settings/', views.profile_settings, name='profile_settings'),
    path('settings/password/', views.change_password, name='change_password'),
    path('verify/', views.agent_verification, name='agent_verification'),
    path('my-buyers/', views.my_buyers, name='my_buyers'),
    path('my-agents/', views.my_agents, name='my_agents'),
    path('report/<int:pk>/', views.report_user, name='report_user'),
    path('admin/', views.admin_overview, name='admin_overview'),
    path('admin/listings/', views.admin_listings, name='admin_listings'),
    path('admin/listings/<int:pk>/approve/', views.admin_approve_listing, name='admin_approve_listing'),
    path('admin/listings/<int:pk>/reject/', views.admin_reject_listing, name='admin_reject_listing'),
    path('admin/verifications/', views.admin_verifications, name='admin_verifications'),
    path('admin/verifications/<int:pk>/approve/', views.admin_approve_verification, name='admin_approve_verification'),
    path('admin/verifications/<int:pk>/reject/', views.admin_reject_verification, name='admin_reject_verification'),
]
