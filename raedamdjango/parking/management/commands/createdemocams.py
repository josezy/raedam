from tenant_schemas.utils import schema_context

from django.core.management.base import BaseCommand
from parking.models import ParkingCamera


cameras_data = [
    {  # River parking
        'geopoint': '-75.378712,6.148837',  # 6ta etapa
        'url': "http://75.147.0.206/mjpg/video.mjpg"
    },
    {  # Good Canadian parking lot
        'geopoint': '-75.378811,6.148104',  # Iglesia
        'url': "http://192.75.71.26/mjpg/video.mjpg"
    },
    {  # Small parking
        'geopoint': '-75.373503,6.147159',
        'url': "http://124.41.68.233:81/cgi-bin/camera"
    },
    {  # Park parking
        'geopoint': '-75.373581,6.146292',
        'url': "http://195.225.70.249/mjpg/video.mjpg"
    }
]


class Command(BaseCommand):
    help = "Create demo camera data for 'devorg' tenant"

    def handle(self, *args, **kwargs):
        with schema_context('devorg'):
            for cam_data in cameras_data:
                ParkingCamera.objects.get_or_create(
                    url=cam_data['url'], defaults=cam_data)
        print("[!] Data created succesfully")
