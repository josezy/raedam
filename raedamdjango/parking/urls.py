from django.urls import path

from parking.views import Parking, Zones, CamListView, add_new_zone, ManageSpots, remove_zone, CamDeleteView, CamCreateView

  
app_name = 'parking'
urlpatterns = [
    path('', Parking.as_view(), name='spots'),
    path('manage_cameras/', CamListView.as_view(), name='manage_cameras'),
    path('zones/', Zones.as_view(), name='zones'),
    path('manage_cameras/new_camera/', CamCreateView.as_view(), name='new_camera'),
    path('manage_cameras/delete_camera/<str:pk>/', CamDeleteView.as_view(), name='delete_camera'),
    path('manage_cameras/manage_spots/<str:pk>/', ManageSpots.as_view(), name='manage_spots'),
    path('manage_cameras/manage_spots/add_new_zone/', add_new_zone, {}, name='add_new_zone'),
    path('manage_cameras/manage_spots/remove_zone/', remove_zone, {}, name='remove_zone')
]
