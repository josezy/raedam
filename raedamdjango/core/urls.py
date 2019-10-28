from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/parking/'), name='home'),
    path('parking/', include(
        ('parking.urls', 'parking'), namespace='parking')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
