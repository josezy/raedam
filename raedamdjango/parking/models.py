from django.db import models
from django.contrib.postgres.fields import ArrayField

from core.models import Camera


class ParkingCamera(Camera):
    spots = ArrayField(ArrayField(models.PositiveIntegerField(), size=4))
