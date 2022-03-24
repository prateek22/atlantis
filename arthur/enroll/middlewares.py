# Django imports
from django.http import HttpResponseBadRequest

# App imports
from .utils import set_tenant_schema_for_request

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            set_tenant_schema_for_request(request)
        except Exception:
            return HttpResponseBadRequest("Failed to set the schema")
        response = self.get_response(request)
        return response