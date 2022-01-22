from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('0GX9kyz622luFVjD5G2W/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('resources.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
