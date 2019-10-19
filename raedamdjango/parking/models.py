from django.db import models
from django.contrib.postgres.fields import ArrayField

from core.model_utils import Camera


class ParkingCamera(Camera):
    spots = ArrayField(ArrayField(
        models.PositiveIntegerField(), size=4), default=list)
