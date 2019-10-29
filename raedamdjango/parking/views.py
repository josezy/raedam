import cv2
import time
import mrcnn
import numpy as np
import tensorflow as tf

from django.db import connection
from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse

from tenant_schemas.utils import schema_context

from typing import Dict, Any
from decimal import Decimal

from core.utils import coords_in_radius
from parking.models import ParkingCamera
from cerebro import load_model, clean_boxes


if settings.ENABLE_DETECTOR and settings.IS_RUNSERVER:
    model = load_model()
    graph = tf.get_default_graph()


class BaseView(View):
    def global_context(self, request=None):
        return {
            'DEBUG': settings.DEBUG,
            'SCHEMA_NAME': connection.schema_name,
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

        with schema_context(request.schema_name):
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
