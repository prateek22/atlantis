from enum import unique
from operator import index
import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType
from django_cassandra_engine.models import DjangoCassandraModel

class Tenant(Model):
    tenant_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    tenant_name = columns.Text(required=True, index=True)
    tenant_domain = columns.Text(required=True, index=True)
    tenant_schema = columns.Text(required=True)

    class _meta:
        app_label = 'enroll'
        model_name = 'Tenant'
    #__type_name__ = 'Tenant'

class TenantMember(Model):
    member_id = columns.UUID(primary_key=True, default=uuid.uuid4, partition_key=True)
    tenant_id = columns.UUID(required=True,partition_key=True) #columns.UserDefinedType(user_type=Tenant)
    member_name = columns.Text(required=True)
    member_username = columns.Text(required=True,index=True)
    member_password = columns.Text(required=True)

    class _meta:
        app_label = 'enroll'
        model_name = 'TenantMember'

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
    
    class _meta:
        app_label = 'enroll'
        model_name = 'EnrolledNode'

    class Meta:
        get_pk_field = 'node_id'

class alerts(Model):

    src_ip = columns.Text(max_length=50, index=True)
    src_port = columns.Text(max_length=50, index=True)
    dest_ip = columns.Text(max_length=50, index=True)
    dest_port = columns.Text(max_length=50, index=True)
    uid = columns.UUID(primary_key=True, default=uuid.uuid4, partition_key=True)


    def __str__(self):
        return "{}:{} => {}:{}".format(self.src_ip, self.src_port, self.dest_ip, self.dest_port)
        
class live_query(Model):
    query = columns.Text(max_length=250)
    tags = columns.UUID(primary_key=True, default=uuid.uuid4, partition_key=True)
    qid = columns.Text(max_length=50, index=True)
    status = columns.Text(max_length=250, index=True)
    
    def __str__(self):
      return self.tags
      
class dist_query_result(Model):
    result_query = columns.Text(max_length=250)
    node_keys = columns.UUID(primary_key=True, default=uuid.uuid4, partition_key=True)
    
    def __str__(self):
      return self.node_keys

class logs(Model):
    log_id = columns.UUID(primary_key=True, default=uuid.uuid4, partition_key=True)
    node_id = columns.UUID(partition_key=True)
    log_type = columns.Text(max_length=50, index=True)
    log_data = columns.Text()
    log_ts = columns.DateTime(index=True)
