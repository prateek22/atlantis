# Django imports
from cassandra.cluster import Cluster

# App imports
from .models import Tenant

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
    cluster = Cluster()
    session = cluster.connect()
    print("Schema: "+schema)
    session.set_keyspace(schema)
    Tenant.__keyspace__ = "db"