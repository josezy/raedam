from django.urls import path
from django.conf.urls import url

from cameras.views import (
   CamListView, delete_camera, CamCreateView, create_new_camera, edit_url_camera, get_camera_position
)

from parking.views import (
   manage_spots
)

app_name = 'cameras'
urlpatterns = [
    path('new_camera/', CamCreateView.as_view(), name='new_camera'),
    path('manage_cameras/', CamListView.as_view(), name='manage_cameras'),
    path('new_camera/create_new_camera/',  create_new_camera, {}, name='create_new_camera'),
    path('edit_url_camera/',  edit_url_camera, {}, name='edit_url_camera'),
    path('get_camera_position/',  get_camera_position, {}, name='get_camera_position'),
    url(r'^manage_cameras/delete_camera/$', delete_camera, name='delete_camera'),

  #  url(r'^manage_cameras/manage_spots/$', manage_spots, name='manage_spots'),    
]