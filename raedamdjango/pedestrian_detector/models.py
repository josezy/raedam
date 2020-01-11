from django.db import models
from cameras.models import Camera
from django.contrib.postgres.fields import ArrayField


class PedestrianCamera(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    detection_zone =ArrayField(
        models.PositiveIntegerField(), size=4)

class PedestrianCamera_reports(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    amount_of_people=models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    



