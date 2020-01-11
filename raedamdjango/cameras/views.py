from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView
from cameras.models import Camera
from pedestrian_detector.models import PedestrianCamera
from parking.models import ParkingCamera
from typing import Dict, Any
from django.db import connection

# Create your views here.

def delete_camera(request):
    if request.method=='GET':
        id_cam = request.GET.get('id_cam')
        print(id_cam)
        camera_of_spots = Camera.objects.get(pk=id_cam)
        camera_of_spots.delete()
        return render(request, 'cam/cam_list.html', {'data':'data'})

def create_new_camera(request):
    url = request.GET.get('url')
    geopoint = request.GET.get('geopoint')
    model_detector = request.GET.get('model_detector')
    new_cam=Camera(url=url,geopoint=geopoint,model_detector=model_detector)
    new_cam.save()

    if(model_detector=='PR'):
        ParkAux=ParkingCamera(camera=new_cam)
        ParkAux.save()
    elif(model_detector=='PD'):
        PedAux=PedestrianCamera(detection_zone=[200,100,200,100],camera=new_cam)
        PedAux.save()

    CAM_DATA = {
        'url': url,
        'geopoint': geopoint
    }
    return JsonResponse(CAM_DATA, safe=False)

def edit_url_camera(request):
    url = request.GET.get('url')
    id_cam = request.GET.get('id_cam')
    CAM_DATA = {
        'url': url
    }
    try:
        camera_of_spots = Camera.objects.get(pk=id_cam)
    except (KeyError, Camera.DoesNotExist):
        CAM_DATA.url= "BAAD"
        return JsonResponse(CAM_DATA, safe=False)
    else:
        camera_of_spots.url=url
        camera_of_spots.save()
    return JsonResponse(CAM_DATA, safe=False)

def get_camera_position(request):
    all_cams=[]
    
    cameras_all = Camera.objects.filter(is_active=True)
    for cam in cameras_all:
        cameras = {
            'shortid': cam.short_id,
            'id_cam': cam.id,
            'coords': cam.coords,
            'model_detector': cam.model_detector,
        }
        all_cams.append(cameras)
    return JsonResponse({'cameras':all_cams }, safe=False)

class BaseView(View):
    def global_context(self, request=None):
        return {
            'DEBUG': settings.DEBUG,
            'view': f'{self.__module__}.{self.__class__.__name__}',
            'sql_queries': len(connection.queries),
        }

    def render_template(self, request, context=None, template=None):
        return render(request, template or self.template, {
            **self.global_context(),
            **(context or {}),
        })

    def render_json(self, json_dict: Dict[str, Any], **kwargs):
        return JsonResponse(json_dict, **kwargs)
        
class CamListView(ListView):
    model = Camera
    template_name = 'cam/cam_list.html'


class CamCreateView(BaseView):
    template = 'cam/cam_add.html'

    def get(self, request):
        return self.render_template(request, {'MAP_API': settings.MAP_API})
        