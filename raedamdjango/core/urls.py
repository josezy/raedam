from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from core.views import Home
from core.admin import AdminLoginView


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('parking/', include(
        ('parking.urls', 'parking'), namespace='parking')),

    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', AdminLoginView.as_view(), name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
