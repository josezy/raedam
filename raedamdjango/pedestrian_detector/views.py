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
from django.utils.dateparse import parse_datetime

from typing import Dict, Any
from decimal import Decimal
# UTILS FUNCTIONS
from core.utils import coords_in_radius
# ALL MODELS
from pedestrian_detector.models import PedestrianCamera_reports
from pedestrian_detector.models import PedestrianCamera
from cameras.models import Camera
# MAIN DETECTON CLASS
from cerebro import load_model, clean_boxes
# IMAGE TO STRING
from django.core.serializers import serialize
import base64
# CHARTS
from datetime import datetime, timedelta
from random import seed
from random import random
from random import randint
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView

if settings.ENABLE_DETECTOR and ~settings.ENABLE_FALSE_DETECTOR and settings.IS_RUNSERVER:
    model = load_model()
    graph = tf.get_default_graph()
# Create your views here.

seed(12)

def manage_detection(request, id_cam):

    data = {'detection_zone': [], 'camera': []}
    detection_zone = PedestrianCamera.objects.filter(camera_id__exact=id_cam)
    camera = Camera.objects.filter(pk=id_cam)
    print(detection_zone)
    detection_zone_json = json.loads(serialize('json', detection_zone))[0]
    camera_json = json.loads(serialize('json', camera))[0]

    detection_zone_json['fields']['detection_zone'] = str(
        detection_zone.values('detection_zone').values()[0]['detection_zone'])

    data['detection_zone'] = detection_zone_json
    data['camera'] = camera_json
    print(data)
    return render(request, 'pedestrian_detector/manage_detection.html', data)


def edit_roi(request):
    id_cam = request.GET.get('id_cam')
    x = request.GET.get('x')
    y = request.GET.get('y')
    width = request.GET.get('width')
    height = request.GET.get('height')
    pedestrian_obj = PedestrianCamera.objects.filter(
        camera_id__exact=id_cam).update(detection_zone=[x, y, width, height])
    return JsonResponse({"ok": "ok"}, safe=False)


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
    pederestian_reports = PedestrianCamera_reports.objects.filter(
        camera_id__exact=cam.id)[0]

    pederestian_reports = json.loads(serialize('json', pederestian_reports))[0]
    print(pederestian_reports)

    result.append({'name': 'name', "data": 'data'})
    return result


class Detection(BaseView):
    def get(self, request):
        lat = Decimal(request.GET.get('latitude'))
        lng = Decimal(request.GET.get('longitude'))

        closest_cams = [
            cam for cam in Camera.objects.filter(is_active=True, model_detector=Camera.PEDESTRIAN)
            if coords_in_radius(
                cam.coords,
                [lng, lat],
                settings.CAMERA_RADIUS
            ) and cam.model_detector == Camera.PEDESTRIAN
        ][:1]  # Hard limit number of detections

        assert len(closest_cams) < 2,\
            'Multiple cameras detection not implemented yet'
        print(closest_cams)

        pedestrian_data = [] if closest_cams else {'error': 'No near cameras'}
        for cam in closest_cams:
           
            print(type(cam.url))
            camera_of_spots = PedestrianCamera.objects.filter(
                camera_id__exact=cam.id)[0]

            cap = cv2.VideoCapture(cam.url)
            success, frame = cap.read()
            if not success:
                pedestrian_data.append({
                    'error': f'Couldnt read frame from camera {cam.short_id}'
                })
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            print(f"[+] Performing detection for cam '{cam.short_id}'")
            detection_start = time.time()
            if settings.ENABLE_FALSE_DETECTOR:
                ammount=randint(3, 10)
                print("\nammount")
                print(ammount)
                cam_info = {
                    'shortid': cam.short_id,
                    'coords': cam.coords,
                    'ammount': ammount,
                    'frame_base64': ""
                }
                park_report_aux = PedestrianCamera_reports(
                    camera=cam, amount_of_people=ammount)
                park_report_aux.save()
                pedestrian_data.append(cam_info)
                pedestrian_data.append(cam_info)
            else:
                with graph.as_default():
                    results = model.detect([rgb_frame], verbose=0)
                print(f"[!] Detection took {time.time() - detection_start} secs")

                boxes = clean_boxes(
                    results[0],
                    settings.PEDESTRIAN_CLS_NAMES,
                    settings.PEDESTRIAN_SCORE
                )
                aux = 0
                for box in boxes:  # Detected cars
                    print(box)
                    y1, x1, y2, x2 = box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                    aux = aux+1

                cam_info = {
                    'shortid': cam.short_id,
                    'coords': cam.coords,
                    'ammount': aux,
                    'frame_base64': ""
                }
                park_report_aux = PedestrianCamera_reports(
                    camera=cam, amount_of_people=cam_info['ammount'])
                park_report_aux.save()
                pedestrian_data.append(cam_info)

                ratio = frame.shape[0] / frame.shape[1]
                resized = cv2.resize(frame, (640, int(ratio * 640)))

                retval, buffer = cv2.imencode('.jpg', resized)
                jpg_as_text = base64.b64encode(buffer)
                txt = str(jpg_as_text)
                cam_info['frame_base64'] = txt[2:-1]
                print(f"{settings.MEDIA_ROOT}/{cam.short_id}.png")
                cv2.imwrite(f"{settings.MEDIA_ROOT}/{cam.short_id}.png", resized)

        return self.render_json(pedestrian_data, safe=False)
# CHARTS


class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""

        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 3, 90, 13, 65]]


line_chart = TemplateView.as_view(template_name='line_chart.html')
line_chart_json = LineChartJSONView.as_view()


def dashboard(request, id_cam):

    today = datetime.now()
    timestamp_to = datetime.now() + timedelta(days=3)
    timestamp_from = datetime.now() - timedelta(days=3)
    print('\ntimestamp_to\n')
    print(timestamp_to)
    print('\ntimestamp_from\n')
    print(timestamp_from)

    # read data
    values = []
    categories=[]

    pedestrian_reports = PedestrianCamera_reports.objects.filter(
        camera_id__exact=id_cam,
        created__gte = timestamp_from,
        created__lt = timestamp_to).distinct()

    pedestrian_reports = json.loads(serialize('json', pedestrian_reports))

    print(pedestrian_reports)
    time_aux=timestamp_from
    aux_avg=0
    count_avg=0
    for i in pedestrian_reports:
        i['fields']['created']=i['fields']['created'][0:-2].replace("T", " ", 1)
        aux_i=datetime.strptime(i['fields']['created'], '%Y-%m-%d %H:%M:%S.%f')
        
        print(aux_i)
        if(aux_i>=time_aux 
            and aux_i<time_aux+timedelta(minutes=15)):
            aux_avg+=i['fields']['amount_of_people']
            count_avg=count_avg+1
            print(count_avg)
        else:
            if(count_avg>0):
                values.append(aux_avg/count_avg)
                categories.append(str(time_aux))
                aux_avg=0
            time_aux=time_aux+timedelta(minutes=15)    

        
    '''for i in pedestrian_reports:
        values.append(i['fields']['amount_of_people'])
        categories.append(i['fields']['created'])'''

    context = {"categories": categories, 'values': values}
    print(context)
    return render(request, 'pedestrian_detector/dashboard.html', context=context)
