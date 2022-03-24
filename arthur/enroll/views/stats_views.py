from pyexpat import model
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from ..models import Tenant, TenantMember
from ..utils import tenant_schema_from_request

class TenantListView(ListView):
    model = Tenant
    context_object_name = 'List of All Tenants'
    template_name = 'enroll/administer/tenants.html'

    def get_queryset(self):
        return Tenant.objects.all()

class TenantMemberListView(ListView):
    model = TenantMember
    context_object_name = 'Active Tenant Members'
    template_name = 'enroll/administer/tenantMembers.html'

    def get_queryset(self):
        return TenantMember.objects.all().using(keyspace=tenant_schema_from_request(self.request)) #filter(tenant_id=self.kwargs['tenant_id'])
