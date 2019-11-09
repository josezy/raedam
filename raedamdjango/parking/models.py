from django.db import models
from django.contrib.postgres.fields import ArrayField

from cameras.models import Camera


class ParkingCamera(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    spots = ArrayField(ArrayField(
        models.PositiveIntegerField(), size=4), default=list)

class ParkingCamera_reports(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    ocupied_spots=models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)