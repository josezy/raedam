from django.urls import path
from django.conf.urls import url

from parking.views import (
    Parking, Zones, add_new_zone, ManageSpots, remove_zone, manage_spots
    
)

app_name = 'parking'
urlpatterns = [
    path('', Parking.as_view(), name='spots'),
    path('zones/', Zones.as_view(), name='zones'),
    path('<str:id_cam>/manage_spots/', manage_spots, name='manage_spots'),   
    path('add_new_zone/', add_new_zone, {}, name='add_new_zone'),
    path('remove_zone/', remove_zone, {}, name='remove_zone')
]
