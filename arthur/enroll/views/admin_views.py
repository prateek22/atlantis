# Django imports
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from cassandra.cqlengine.management import create_keyspace_simple, sync_table

# App imports
from ..models import EnrolledNode, Tenant, TenantMember, alerts, dist_query_result, live_query
from ..forms.tenantForm import TenantForm
from ..forms.tenantMemberForm import TenantMemberForm
from ..settings import *

#Miscellaneous imports
from passlib.hash import pbkdf2_sha256
import os

# Endpoint for registering new nodes
def addTenantMember(request):
    if request.method == 'GET':
        form = TenantMemberForm()
        #form.helper.build_default_layout()
        #form.tenant.choices = [(tenant.tenant_name, tenant.tenant_name) for tenant in Tenant.objects().all()]
        return render(request, 'enroll/administer/add_tenant_member.html', {'form': form})
    elif request.method == 'POST':
        form = TenantMemberForm(request.POST)
        if form.is_valid():
            member_name = form.cleaned_data['member_name']
            member_username = form.cleaned_data['member_email']
            member_password = form.cleaned_data['member_password']
            tenant_name = form.cleaned_data['tenant']
        tenant = Tenant.objects(tenant_name=tenant_name)
        if not tenant:
            raise HttpResponseBadRequest("Invalid details!!")
        else:
            tenant = tenant[0]
        tenantMember = TenantMember.objects(member_username=member_username)
        if tenantMember:
            raise HttpResponseBadRequest("Invalid details!!")
        member_password_hash = pbkdf2_sha256.hash(member_password)
        tenantMember = TenantMember(member_name=member_name, member_username=member_username, member_password=member_password_hash, tenant_id=tenant.tenant_id)
        tenantMember.__keyspace__= tenant.tenant_domain
        tenantMember.save()
        context = {"message": 'Tenant member {} added successfully!!'.format(member_username)}
        return render(request, 'enroll/miscellaneous/success.html', context)

def addTenant(request):
    if request.method == 'GET':
        form = TenantForm()
        return render(request, 'enroll/administer/add_tenant.html', {'form': form})
    elif request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            tenant_name = form.cleaned_data['tenant_name']
            tenant_domain = form.cleaned_data['tenant_domain']
        tenant = Tenant.objects(tenant_name=tenant_name)
        if tenant:
            raise HttpResponseBadRequest("Invalid details!!")
        tenant = Tenant(tenant_name=tenant_name, tenant_domain=tenant_domain)
        tenant.save()
        create_keyspace_simple(tenant_domain,replication_factor=1)
        #sync_type(ks_name=tenant_domain, type_model=Tenant)
        sync_table(keyspaces=[tenant_domain], model=TenantMember)
        sync_table(keyspaces=[tenant_domain], model=EnrolledNode)
        sync_table(keyspaces=[tenant_domain], model=alerts)
        sync_table(keyspaces=[tenant_domain], model=live_query)
        sync_table(keyspaces=[tenant_domain], model=dist_query_result)
        TenantMemberForm()
        os.system("../scripts/generate_new_cert.sh " + tenant_domain)
        os.system("echo '127.0.0.1   " + tenant_domain + ".edr.api' >> /etc/hosts")
        context = {"message": 'Tenant {} added successfully!!'.format(tenant_name)}
        return render(request, 'enroll/miscellaneous/success.html', context)