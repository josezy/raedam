from django.db import models
from django.utils.functional import cached_property

from decimal import Decimal

from core.model_utils import BaseModel


class Camera(BaseModel):
    url = models.URLField()
    # Always use the format 'lon.gitude,lat.itude'
    geopoint = models.CharField(max_length=100)

    @cached_property
    def coords(self):
        return list(map(lambda x: Decimal(x), self.geopoint.split(',')))
