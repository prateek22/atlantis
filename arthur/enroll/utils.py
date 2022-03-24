# Django imports
from cassandra.cluster import Cluster
from django.db import connection, connections
from django_cassandra_engine.connection import Cursor

# App imports
from .models import EnrolledNode, Tenant, TenantMember, alerts, dist_query_result, live_query

def get_tenants_schema(hostname):
    if hostname == 'admin':
        return 'db'
    tenant = Tenant.objects(tenant_domain=hostname)
    if tenant:
        return tenant[0].tenant_schema
    else:
        raise Exception("Invalid details!!")

def hostname_from_request(request):
    # split on `:` to remove port
    return request.get_host().split(':')[0].split('.')[0].lower()

def tenant_schema_from_request(request):
    hostname = hostname_from_request(request)
    try:
        schema = get_tenants_schema(hostname)
    except Exception:
        raise Exception("Invalid details!!")
    return schema

def set_tenant_schema_for_request(request):
    try:
        schema = tenant_schema_from_request(request)
    except Exception:
        raise Exception("Invalid details!!")
    Tenant.__keyspace__ = "db"
    TenantMember.__keyspace__ = schema
    EnrolledNode.__keyspace__ = schema
    alerts.__keyspace__ = schema
    live_query.__keyspace__ = schema
    dist_query_result.__keyspace__ = schema