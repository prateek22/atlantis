# Imports for authentication
# For Authentication
import jwt
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.contrib.auth.management.commands import createsuperuser
from django.db import models #: Instead of model data types, we will be using columns module to specify the datatypes


from enum import unique
from operator import index
import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
# from cassandra.cqlengine.usertype import UserType
# from django_cassandra_engine.models import DjangoCassandraModel

# Authentication Model

class TenantMemberManager(BaseUserManager):
    # https://thinkster.io/tutorials/django-json-api/authentication
    def create_user(self, username, email, tenant_id, password=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        if password is None:
            raise TypeError('Users must have a password.')

        if tenant_id is None:
            raise TypeError('Users must have a tenant.')

        user = self.model(username=username, email=self.normalize_email(email), tenant_id=tenant_id)
        user.set_password(password)
        user.is_superuser = True
        user.save()

        return user

    def create_superuser(self, username, email, tenant_id, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, tenant_id, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class TenantMember(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField() #columns.UserDefinedType(user_type=Tenant)
    username = models.TextField(db_index=True, max_length=255, unique=True)
    email = models.TextField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'tenant_id']

    objects = TenantMemberManager()

    class Meta:
        unique_together = (('id', 'tenant_id'),)

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.email

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return self.username

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.username

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.email,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

# Cassandra Models

class Tenant(Model):
    tenant_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    tenant_name = columns.Text(required=True, index=True)
    tenant_domain = columns.Text(required=True, index=True)
    tenant_schema = columns.Text(required=True)

    class _meta:
        app_label = 'enroll'
        model_name = 'Tenant'
    #__type_name__ = 'Tenant'


class EnrolledNode(Model):
    node_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    tenant_id = columns.UUID(required=True, primary_key=True, partition_key=True, index=True) #columns.UserDefinedType(user_type=Tenant)
    node_system_id = columns.Text(required=True, index=True)
    node_os = columns.Text(required=True)
    node_arch = columns.Text(required=True)
    node_secret = columns.Text(required=True)
    node_hash = columns.Text(required=True)
    node_address = columns.Text(required=True, index=True, default='127.0.0.1')
    node_info = columns.Text()
    
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
