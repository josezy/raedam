from django.urls import path
from django.conf.urls import url

from pederastian_detector.views import (
   manage_detection, edit_roi, Detection, get_reports
)


app_name = 'pederestian_detector'
urlpatterns = [
    path('<str:id_cam>/manage_detection/', manage_detection, name='manage_detection'),   

    path('detection/', Detection.as_view(), name='detection'),
    path('get_reports/', get_reports, {}, name='get_reports'),
    path('edit_roi/', edit_roi, {}, name='edit_roi'),
  #  url(r'^manage_cameras/manage_spots/$', manage_spots, name='manage_spots'),    
]