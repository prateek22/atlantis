from enum import unique
import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType
from django_cassandra_engine.models import DjangoCassandraModel

class Tenant(Model):
    tenant_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    tenant_name = columns.Text(required=True)
    tenant_domain = columns.Text(required=True)
    #__type_name__ = 'Tenant'

class TenantMember(Model):
    member_id = columns.UUID(primary_key=True, default=uuid.uuid4, partition_key=True)
    tenant_id = columns.UUID(required=True,partition_key=True) #columns.UserDefinedType(user_type=Tenant)
    member_name = columns.Text(required=True)
    member_username = columns.Text(required=True)
    member_password = columns.Text(required=True)

    class Meta:
        get_pk_field = 'member_id'

class EnrolledNode(Model):
    node_id = columns.UUID(primary_key=True, default=uuid.uuid4, partition_key=True)
    tenant_id = columns.UUID(required=True,partition_key=True, index=True) #columns.UserDefinedType(user_type=Tenant)
    node_system_id = columns.Text(required=True, index=True)
    node_os = columns.Text(required=True)
    node_arch = columns.Text(required=True)
    node_secret = columns.Text(required=True)
    node_hash = columns.Text(required=True)
    node_address = columns.Text(required=True, index=True, default='127.0.0.1')

    class Meta:
        get_pk_field = 'node_id'

class alerts(Model):

    src_ip = columns.Text(max_length=50)
    src_port = columns.Text(max_length=50)
    dest_ip = columns.Text(max_length=50)
    dest_port = columns.Text(max_length=50)
    uid = columns.UUID(primary_key=True, default=uuid.uuid4, partition_key=True)


    def __str__(self):
        return "{}:{} => {}:{}".format(self.src_ip, self.src_port, self.dest_ip, self.dest_port)
        
class live_query(Model):
    query = columns.Text(max_length=250)
    query_id = columns.UUID(primary_key=True, default=uuid.uuid4, partition_key=True)
    
    def __str__(self):
      return self.query_id
      
class dist_query_result(Model):
    result_query = columns.Text(max_length=250)
    node_keys = columns.UUID(primary_key=True, default=uuid.uuid4, partition_key=True)
    
    def __str__(self):
      return self.node_keys
