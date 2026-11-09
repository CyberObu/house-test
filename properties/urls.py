from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.property_list, name='list'),
    path('map/', views.property_map, name='map'),
    path('compare/', views.compare_view, name='compare'),
    path('compare/clear/', views.compare_clear, name='compare_clear'),
    path('compare/add/<slug:slug>/', views.compare_add, name='compare_add'),
    path('compare/remove/<slug:slug>/', views.compare_remove, name='compare_remove'),
    path('save-search/', views.save_search, name='save_search'),
    path('saved-search/<int:pk>/delete/', views.delete_saved_search, name='delete_saved_search'),
    path('neighborhoods/', views.all_neighborhoods, name='neighborhoods'),
    path('neighborhood/<str:city>/', views.neighborhood, name='neighborhood'),
    path('type/<slug:slug>/', views.property_type_list, name='by_type'),
    path('<slug:slug>/', views.property_detail, name='detail'),
    path('<slug:slug>/favorite/', views.toggle_favorite, name='favorite'),
]
