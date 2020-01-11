from django.urls import path
from django.conf.urls import url

from pedestrian_detector.views import (
   manage_detection, edit_roi, Detection, get_reports, LineChartJSONView, TemplateView,dashboard
)


line_chart = TemplateView.as_view(template_name='pedestrian_detector/manage_detection.html')
line_chart_json = LineChartJSONView.as_view()

app_name = 'pedestrian_detector'
urlpatterns = [
    path('<str:id_cam>/manage_detection/', manage_detection, name='manage_detection'),  
    path('<str:id_cam>/dashboard/', dashboard, name='dashboard'), 

    path('detection/', Detection.as_view(), name='detection'),
    path('line_chart_json/', line_chart_json, name='line_chart_json'),
    path('get_reports/', get_reports, {}, name='get_reports'),
    path('edit_roi/', edit_roi, {}, name='edit_roi'),
  #  url(r'^manage_cameras/manage_spots/$', manage_spots, name='manage_spots'),    
]