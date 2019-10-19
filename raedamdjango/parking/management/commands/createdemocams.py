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
]


class Command(BaseCommand):
    help = 'Create demo cameras data for testing'

    def handle(self, *args, **kwargs):
        for cam_data in cameras_data:
            ParkingCamera.objects.get_or_create(
                url=cam_data['url'], defaults=cam_data)
        print("[!] Data created succesfully")
