from pyexpat import model
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from ..models import Tenant, TenantMember

class TenantListView(ListView):
    model = Tenant
    context_object_name = 'List of All Tenants'

class TenantMemberListView(ListView):
    model = TenantMember
    context_object_name = 'Active Tenant Members'

    def get_queryset(self):
        return TenantMember.objects.filter(tenant_id=self.kwargs['tenant_id'])
