from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from django.contrib.auth.models import AbstractUser

from tenant_schemas.models import TenantMixin

from core.model_utils import BaseModel


class Organization(BaseModel, TenantMixin):
    # id: models.UUIDField
    # schema_name: models.CharField
    # created: models.DateTimeField
    # updated: models.DateTimeField

    name = models.CharField(max_length=100, unique=True)
    notes = models.TextField(null=True, blank=True)

    user_set: models.Manager

    class Meta:
        verbose_name = 'Tucano Organization'
        verbose_name_plural = 'Tucano Organizations'

    def __str__(self):
        extra_info = ' (god org)' if self.is_god_org else ''
        return f"Organization: {self.name}{extra_info}"

    @cached_property
    def is_god_org(self):
        return self.name == 'public'

    @cached_property
    def domain_url(self):
        return settings.DEFAULT_HOST

    @cached_property
    def users(self):
        return (
            User.objects
                .using('public')
                .filter(organization_id=self.id)
        )

    @cached_property
    def admins(self):
        return (
            User.objects
                .using('public')
                .filter(organization_id=self.id, is_superuser=True)
        )


class User(AbstractUser, BaseModel):
    # id = models.UUIDField
    # username: models.CharField
    # password: models.PasswordField
    # email: models.EmailField
    # first_name: models.CharField
    # last_name: models.CharField

    # is_active: models.BooleanField
    # is_staff: models.BooleanField
    # is_superuser: models.BooleanField
    # last_login: models.DateTimeField
    # date_joined: models.DateTimeField
    # created: models.DateTimeField
    # updated: models.DateTimeField

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    debug_toolbar = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Tucano User'
        verbose_name_plural = 'Tucano Users'

    @cached_property
    def org(self):
        return self.organization

    @cached_property
    def is_god(self):
        return self.organization.is_god_org
