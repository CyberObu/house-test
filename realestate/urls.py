from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('properties/', include('properties.urls')),
    path('agents/', include('agents.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('platform/', include('dashboard.urls_platform')),
    path('blog/', include('blog.urls')),
    path('messages/', include('messaging.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
