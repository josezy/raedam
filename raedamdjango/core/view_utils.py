from django.views import View
from django.conf import settings
from django.db import connection
from django.shortcuts import render
from django.http import JsonResponse

from typing import Dict, Any


class BaseView(View):
    def global_context(self, request=None):
        return {
            'DEBUG': settings.DEBUG,
            'SCHEMA_NAME': connection.schema_name,
            'view': f'{self.__module__}.{self.__class__.__name__}',
            'sql_queries': len(connection.queries),
        }

    def render_template(self, request, context=None, template=None):
        return render(request, template or self.template, {
            **self.global_context(),
            **(context or {}),
        })

    def render_json(self, json_dict: Dict[str, Any], **kwargs):
        return JsonResponse(json_dict, **kwargs)
