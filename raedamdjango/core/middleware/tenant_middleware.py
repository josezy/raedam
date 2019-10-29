from django.conf import settings

from tenant_schemas.middleware import DefaultTenantMiddleware

from core.models import Organization


class TenantMiddleware(DefaultTenantMiddleware):
    DEFAULT_SCHEMA_NAME = settings.DEFAULT_SCHEMA_NAME

    def get_tenant(self, model, hostname, request):
        if request.user.is_authenticated:
            org = request.user.organization
        else:
            org = Organization.objects.get(schema_name='public')

        request.schema_name = org.schema_name
        return org

    def process_response(self, request, response):
        response['X-HTTP-TENANT'] = request.schema_name
        return response
