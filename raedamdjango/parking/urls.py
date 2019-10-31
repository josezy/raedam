from django.urls import path

from parking.views import (
    Parking, Zones, CamListView, add_new_zone, ManageSpots, remove_zone,
    CamDeleteView, CamCreateView, create_new_camera, edit_url_camera
)

app_name = 'parking'
urlpatterns = [
    path('', Parking.as_view(), name='spots'),
    path('manage_cameras/', CamListView.as_view(), name='manage_cameras'),
    path('zones/', Zones.as_view(), name='zones'),
    path('new_camera/', CamCreateView.as_view(), name='new_camera'),
    path('new_camera/create_new_camera/',  create_new_camera, {}, name='create_new_camera'),
    path('delete_camera/<str:pk>/', CamDeleteView.as_view(), name='delete_camera'),
    path('manage_spots/<str:pk>/', ManageSpots.as_view(), name='manage_spots'),
    
    path('edit_url_camera/', edit_url_camera, {} , name='edit_url_camera'),
    path('add_new_zone/', add_new_zone, {}, name='add_new_zone'),
    path('remove_zone/', remove_zone, {}, name='remove_zone')
]
