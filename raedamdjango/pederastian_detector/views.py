import cv2
import json
import time
import mrcnn
import numpy as np
import tensorflow as tf

from django.db import connection
from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse

from typing import Dict, Any
from decimal import Decimal

from core.utils import coords_in_radius
from pederastian_detector.models import PederastianCamera_reports
from pederastian_detector.models import PederastianCamera
from cameras.models import Camera
from cerebro import load_model, clean_boxes

from django.core.serializers import serialize
import base64

if settings.ENABLE_DETECTOR and settings.IS_RUNSERVER:
    model = load_model()
    graph = tf.get_default_graph()
# Create your views here.
def manage_detection(request,id_cam):
    
    data={'detection_zone':[],'camera': []}
    detection_zone = PederastianCamera.objects.filter(camera_id__exact=id_cam)
    camera = Camera.objects.filter(pk=id_cam)
    print(detection_zone)
    detection_zone_json=json.loads(serialize('json', detection_zone))[0]
    camera_json=json.loads(serialize('json', camera))[0]
    
    detection_zone_json['fields']['detection_zone']=str(detection_zone.values('detection_zone').values()[0]['detection_zone'])
    
    data['detection_zone']=detection_zone_json
    data['camera']=camera_json
    print(data)
    return render(request, 'pederastian_detector/manage_detection.html', data)

def edit_roi(request):
    id_cam = request.GET.get('id_cam')
    x = request.GET.get('x')
    y = request.GET.get('y')
    width = request.GET.get('width')
    height = request.GET.get('height')
    pederastian_obj = PederastianCamera.objects.filter(camera_id__exact=id_cam).update(detection_zone=[x,y,width,height])
    return JsonResponse({"ok":"ok"}, safe=False)


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
        
def get_reports(request):
    result = []
    pederestian_reports = PederastianCamera_reports.objects.filter(camera_id__exact=cam.id)[0]

    pederestian_reports=json.loads(serialize('json', pederestian_reports))[0]
    print(pederestian_reports)

    result.append({'name': 'name', "data": 'data'})
    return result

class Detection(BaseView):
    def get(self, request):
        lat = Decimal(request.GET.get('latitude'))
        lng = Decimal(request.GET.get('longitude'))

        closest_cams = [
            cam for cam in Camera.objects.filter(is_active=True,model_detector=Camera.PEDERASTIAN)
            if coords_in_radius(
                cam.coords,
                [lng, lat],
                settings.CAMERA_RADIUS
            ) and cam.model_detector==Camera.PEDERASTIAN
        ][:1]  # Hard limit number of detections

        assert len(closest_cams) < 2,\
            'Multiple cameras detection not implemented yet'
        print(closest_cams)

        pederastian_data = [] if closest_cams else {'error': 'No near cameras'}
        for cam in closest_cams:
            print(type(cam.url))
            camera_of_spots = PederastianCamera.objects.filter(camera_id__exact=cam.id)[0]

            cap = cv2.VideoCapture(cam.url)
            success, frame = cap.read()
            if not success:
                pederastian_data.append({
                    'error': f'Couldnt read frame from camera {cam.short_id}'
                })
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            print(f"[+] Performing detection for cam '{cam.short_id}'")
            detection_start = time.time()
            with graph.as_default():
                results = model.detect([rgb_frame], verbose=0)
            print(f"[!] Detection took {time.time() - detection_start} secs")

            boxes = clean_boxes(
                results[0],
                settings.PEDERASTIAN_CLS_NAMES,
                settings.PEDERASTIAN_SCORE
            )
            aux=0
            for box in boxes:  # Detected cars
                print(box)
                y1, x1, y2, x2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                aux=aux+1

            
            
            cam_info = {
                'shortid': cam.short_id,
                'coords': cam.coords,
                'ammount': aux,
                'frame_base64': ""
            }
            park_report_aux=PederastianCamera_reports(camera=cam,amount_of_people=cam_info['ammount'])
            park_report_aux.save()
            pederastian_data.append(cam_info)


            ratio = frame.shape[0] / frame.shape[1]
            resized = cv2.resize(frame, (640, int(ratio * 640)))

            retval, buffer = cv2.imencode('.jpg', resized)
            jpg_as_text = base64.b64encode(buffer)
            txt=str(jpg_as_text)
            cam_info['frame_base64']=txt[2:-1]
            print(f"{settings.MEDIA_ROOT}/{cam.short_id}.png")
            cv2.imwrite(f"{settings.MEDIA_ROOT}/{cam.short_id}.png", resized)

        return self.render_json(pederastian_data, safe=False)
