from django.db import models
from core.model_utils import BaseModel
from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from decimal import Decimal


class Camera(BaseModel):

    PARKING = 'PR'
    PEDESTRIAN = 'PD'
    MODEL_DETECTOR = [
        (PARKING, 'Parking'),
        (PEDESTRIAN, 'Pedestrian'),
    ]
    model_detector = models.CharField(
        max_length=2,
        choices=MODEL_DETECTOR,
        default=PARKING,
    )

    url = models.URLField(unique=True)
    # Always use the format 'lon.gitude,lat.itude'
    geopoint = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    @cached_property
    def coords(self):
        return list(map(lambda x: Decimal(x), self.geopoint.split(',')))

    @cached_property
    def last_frame(self):
        return f"{settings.MEDIA_URL}{self.short_id}.png"

