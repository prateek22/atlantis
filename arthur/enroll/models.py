import uuid
from cassandra.cqlengine import columns
from django_cassandra_engine.models import DjangoCassandraModel

# class Tenant(DjangoCassandraModel):
#     tenant_id = columns.UUID(primary_key=True, default=uuid.uuid4)
#     tenant_name = columns.Text(required=True)
#     tenant_domain = columns.Text(required=True)

# class TenantMember(DjangoCassandraModel):
#     member_id = columns.UUID(primary_key=True, default=uuid.uuid4)
#     tenant_id = columns.UserDefinedType(user_type=Tenant)
#     member_name = columns.Text(required=True)
#     member_username = columns.Text(required=True)
#     member_password = columns.Text(required=True)

# class Host(DjangoCassandraModel):
#     host_id = columns.UUID(primary_key=True, default=uuid.uuid4)
#     tenant_id = columns.UserDefinedType(user_type=Tenant)
#     host_system_id = columns.Text(required=True)
#     host_os = columns.Text(required=True)
#     host_arch = columns.Text(required=True)
#     host_secret = columns.Text(required=True)
#     host_hash = columns.Text(required=True)

# class ExampleModel(DjangoCassandraModel):
#     example_id   = columns.UUID(primary_key=True, default=uuid.uuid4)
#     example_type = columns.Integer(index=True)
#     created_at   = columns.DateTime()
#     description  = columns.Text(required=False)
