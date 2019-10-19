from django.urls import path

from parking.views import Parking, Zones


urlpatterns = [
    path('', Parking.as_view(), name='spots'),
    path('zones/', Zones.as_view(), name='zones')
]
