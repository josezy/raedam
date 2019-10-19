from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/parking/'), name='home'),
    path('parking/', include(
        ('parking.urls', 'parking'), namespace='parking')),
    path('admin/', admin.site.urls),
]
