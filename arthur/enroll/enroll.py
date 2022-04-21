# Django imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.validators import RegexValidator
from django.http import HttpResponse, HttpResponseBadRequest

# App imports
from .models import EnrolledNode, Tenant

#Miscellaneous imports
import secrets, hashlib, base64, os, binascii, json
from passlib.hash import pbkdf2_sha256

class Enrollment():
    tenant_id = None
    node_system_id = None
    node = None

    def __init__(self, tenant_id, node_system_id):
        self.tenant_id = tenant_id
        self.node_system_id = node_system_id
        if tenant_id != None and node_system_id != None:
            self.node = EnrolledNode.objects(node_system_id=self.node_system_id, tenant_id=self.tenant_id)
            print("here")

    def generate_node(self, node_os, node_arch):
        if self.node:
            self.node = self.node[0]
            return self.node.node_secret
        else:
            m = hashlib.sha256()
            salt = os.urandom(32)
            secret = '{"node_system_id":"' + self.node_system_id + '", "tenant_id": "' + self.tenant_id + '", "secret":"'+ self.generate_node_secret() + '"}'
            encoded_secret = base64.b64encode(secret.encode())
            encoded_secret_string = encoded_secret.decode('utf-8')
            print(type(encoded_secret))
            node_hash = pbkdf2_sha256.hash(encoded_secret_string)
            #print(host_hash.decode('ascii'))
            tenant = Tenant.objects(tenant_id=self.tenant_id)
            if tenant:
                tenant = tenant[0]
            else:
                return None
            self.node = EnrolledNode(tenant_id=self.tenant_id, node_system_id=self.node_system_id, node_os=node_os, node_arch=node_arch, node_secret=encoded_secret_string, node_hash=node_hash)
            self.node.save()
            return encoded_secret_string

    def generate_node_secret(self):
        secret = secrets.token_hex(16)
        return secret

    def update_node_address(self, address):

        self.node.update(node_address = address)
        return self.node.node_id

    def validate_enroll_secret(self, enroll_secret):
        decoded_secret = base64.b64decode(enroll_secret.encode())
        secret = json.loads(decoded_secret.decode())
        tenant = Tenant.objects(tenant_id=secret['tenant_id'])
        if tenant:
            tenant = tenant[0]
        else:
            raise Exception("Invalid details!!")
        node = EnrolledNode.objects(node_system_id=secret['node_system_id'])
        if node:
            self.node = node[0]
        if not pbkdf2_sha256.verify(enroll_secret, self.node.node_hash):
            return None
        else:
            return self.node

    def validate_node(self, address, node_id):
        node = EnrolledNode.objects(node_address=address)
        if node:
            self.node = node[0]
            return self.node
        else:
            return None

        # if node and not pbkdf2_sha256.verify(enroll_secret, self.node.node_hash):
        #     return None
        # else:
        #     return self.node


    def get_enrolled_nodes():

        return [row.node_address for row in EnrolledNode.objects.all()]