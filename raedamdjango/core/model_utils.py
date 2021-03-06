import uuid
from typing import Dict, Any

from django.db import models
from django.conf import settings
from django.utils.functional import cached_property

from tenant_schemas.models import TenantQueryset

from decimal import Decimal


DANGEROUS_ATTRS = ('password',)


def get_short_uuid(uuid) -> str:
    """get the first block of a 4-word UUID to use as a short identifier"""
    full_uuid = str(uuid)
    return full_uuid.split('-', 1)[0]


class BaseModel(models.Model):
    objects: models.Manager

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def short_id(self) -> str:
        return get_short_uuid(self.id)

    @property
    def field_names(self):
        return [
            getattr(field, 'attname', getattr(field, 'name'))
            for field in self._meta.get_fields()
            if field.concrete and getattr(field, 'name')
        ]

    def attrs(self, *attrs) -> Dict[str, Any]:
        """
        get a dictionary of attr:val for a list of attrs
        """
        safe_attrs = (
            attr for attr in attrs or self.field_names
            if attr not in DANGEROUS_ATTRS
        )
        return {
            attr: getattr(self, attr, getattr(self, f'{attr}_set', None))
            for attr in safe_attrs
        }

    def __json__(self, *attrs) -> Dict[str, Any]:
        return {
            'type': f'{self.__class__.__module__}.{self.__class__.__name__}',
            'id': self.id,
            'str': str(self),
            **self.attrs(*attrs),
        }

    def __str__(self):
        return f'{self.__class__.__name__}:{self.short_id}'

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.short_id}>'

    class Meta:
        abstract = True


class Camera(BaseModel):
    objects = TenantQueryset.as_manager()

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

    class Meta:
        abstract = True
