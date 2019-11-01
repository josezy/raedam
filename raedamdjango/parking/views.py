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
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy

from typing import Dict, Any
from decimal import Decimal

from core.utils import coords_in_radius
from parking.models import ParkingCamera
from cerebro import load_model, clean_boxes


if settings.ENABLE_DETECTOR and settings.IS_RUNSERVER:
    model = load_model()
    graph = tf.get_default_graph()


def manage_spots(request, cam_id):
    return render(request, 'parking/manage_spots.html', {'probe': "probe"})


def remove_zone(request):
    SPOT_DATA = json.loads(request.GET.get('SPOT_DATA'))
    camera_of_spots = ParkingCamera.objects.get(pk=SPOT_DATA['id_cam'])
    camera_of_spots.spots = SPOT_DATA['spots']
    camera_of_spots.save()
    return JsonResponse(SPOT_DATA, safe=False)

def create_new_camera(request):
    url = request.GET.get('url')
    geopoint = request.GET.get('geopoint')
    new_cam=ParkingCamera(url=url,geopoint=geopoint)
    new_cam.save()
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
        camera_of_spots = ParkingCamera.objects.get(pk=id_cam)
    except (KeyError, ParkingCamera.DoesNotExist):
        return JsonResponse(zone_data, safe=False)
    else:
        camera_of_spots.url=url
        camera_of_spots.save()
    return JsonResponse(CAM_DATA, safe=False)
def add_new_zone(request):
    SPOT_DATA = json.loads(request.GET.get('SPOT_DATA'))
    id_cam = SPOT_DATA['id_cam']
    x = SPOT_DATA['x']
    y = SPOT_DATA['y']
    width = SPOT_DATA['width']
    height = SPOT_DATA['height']
    zone_data = {
        'id_cam': id_cam,
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'spots': [],
    }

    try:
        camera_of_spots = ParkingCamera.objects.get(pk=id_cam)
    except (KeyError, ParkingCamera.DoesNotExist):
        return JsonResponse(zone_data, safe=False)
    else:
        camera_of_spots.spots.append([x, y, width, height])
        camera_of_spots.save()

    zone_data['spots'] = camera_of_spots.spots
    return JsonResponse(zone_data, safe=False)


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


class CamDeleteView(DeleteView):
    model = ParkingCamera
    template_name = 'parking/cam_delete.html'
    success_url = reverse_lazy('parking:manage_spots')


class CamListView(ListView):
    model = ParkingCamera
    template_name = 'parking/cam_list.html'


class ManageSpots(UpdateView):
    model = ParkingCamera
    fields = ('spots', 'geopoint',)
    template_name = 'parking/manage_spots.html'


class CamCreateView(BaseView):
    template = 'parking/cam_add.html'

    def get(self, request):
        return self.render_template(request, {'MAP_API': settings.MAP_API})


class Parking(BaseView):
    template = 'parking/home.html'

    def context(self):
        return {
            'MAP_API': settings.MAP_API,
            'FETCH_ZONES_INTERVAL': settings.FETCH_ZONES_INTERVAL,
            'MAX_ZONE_REQUESTS': settings.MAX_ZONE_REQUESTS,
        }

    def get(self, request):
        return self.render_template(request, self.context())


class Zones(BaseView):
    def get(self, request):
        lat = Decimal(request.GET.get('latitude'))
        lng = Decimal(request.GET.get('longitude'))

        closest_cams = [
            cam for cam in ParkingCamera.objects.filter(is_active=True)
            if coords_in_radius(
                cam.coords,
                [lng, lat],
                settings.CAMERA_RADIUS
            )
        ][:1]  # Hard limit number of detections

        assert len(closest_cams) < 2,\
            'Multiple cameras detection not implemented yet'

        parking_data = [] if closest_cams else {'error': 'No near cameras'}
        for cam in closest_cams:
            if not cam.spots:
                parking_data.append({
                    'error': f'ParkingCamera {cam.short_id} hasnt marked spots'
                })
                continue

            cap = cv2.VideoCapture(cam.url)
            success, frame = cap.read()
            if not success:
                parking_data.append({
                    'error': f'Couldnt read frame from camera {cam.short_id}'
                })
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            print(f"[+] Performing detection for cam '{cam.short_id}'")
            detection_start = time.time()
            with graph.as_default():
                results = model.detect([rgb_frame], verbose=0)
            print(f"[!] Detection took {time.time() - detection_start} secs")

            car_boxes = clean_boxes(
                results[0],
                settings.CAR_CLS_NAMES,
                settings.CAR_SCORE
            )
            car_spots = np.array(cam.spots)
            overlaps = mrcnn.utils.compute_overlaps(car_spots, car_boxes)

            for car_box in car_boxes:  # Detected cars
                y1, x1, y2, x2 = car_box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)

            cam_spots = {
                'shortid': cam.short_id,
                'coords': cam.coords,
                'total_spots': len(cam.spots),
                'free_spots': 0,
                'frame': cam.last_frame,
            }
            # Car spots
            for car_spot, overlap_areas in zip(car_spots, overlaps):
                y1, x1, y2, x2 = car_spot
                center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                radius = int((y2 - y1) / 2)
                free_spot = np.max(overlap_areas) < 0.2
                color = (0, 255, 0) if free_spot else (0, 0, 255)
                cam_spots['free_spots'] += 1 if free_spot else 0
                cv2.circle(frame, center, radius, color, 3)

            assert cam_spots['free_spots'] <= cam_spots['total_spots'],\
                f"'free_spots' ({cam_spots['free_spots']}) can't never "\
                f"be greater than 'total_spots' ({cam_spots['total_spots']})"

            parking_data.append(cam_spots)
            ratio = frame.shape[0] / frame.shape[1]
            resized = cv2.resize(frame, (640, int(ratio * 640)))
            cv2.imwrite(f"{settings.MEDIA_ROOT}/{cam.short_id}.png", resized)

        return self.render_json(parking_data, safe=False)
