from django.core.management.base import BaseCommand
from cameras.models import Camera
from parking.models import ParkingCamera
from pederastian_detector.models import PederastianCamera

cameras_data = [
    {  # River parking
        'geopoint': '-75.378712,6.148837',  # 6ta etapa
        'url': "http://75.147.0.206/mjpg/video.mjpg",
        'model_detector':Camera.PARKING

    },
    {  # Good Canadian parking lot
        'geopoint': '-75.378811,6.148104',  # Iglesia
        'url': "http://192.75.71.26/mjpg/video.mjpg",
        'model_detector':Camera.PEDERESTIAN
    },
    {  # Small parking
        'geopoint': '-75.373503,6.147159',
        'url': "http://124.41.68.233:81/cgi-bin/camera",
        'model_detector':Camera.PARKING
    },
    {  # Park parking
        'geopoint': '-75.373581,6.146292',
        'url': "http://195.225.70.249/mjpg/video.mjpg",
        'model_detector':Camera.PARKING
    }
]


class Command(BaseCommand):
    help = 'Create demo cameras data for testing'

    def handle(self, *args, **kwargs):
        for cam_data in cameras_data:
            Camera.objects.get_or_create(
                url=cam_data['url'], model_detector=cam_data['model_detector'], defaults=cam_data)
        for cameras in Camera.objects.all():
            print(cameras.model_detector)
            if(cameras.model_detector=='PR'):
                ParkAux=ParkingCamera(camera=cameras)
                ParkAux.save()
            elif(cameras.model_detector=='PD'):
                PedAux=PederastianCamera(detection_zone=[200,100,200,100],camera=cameras)
                PedAux.save()
        print("[!] Data created succesfully")
