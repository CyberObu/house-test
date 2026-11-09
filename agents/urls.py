from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    path('', views.agent_list, name='list'),
    path('agencies/', views.agency_list, name='agency_list'),
    path('agencies/<slug:slug>/', views.agency_detail, name='agency_detail'),
    path('<int:pk>/', views.agent_detail, name='detail'),
]
