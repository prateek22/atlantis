from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.validators import RegexValidator
from .models import EnrolledNode
import secrets, hashlib, base64, os, binascii, json
from passlib.hash import pbkdf2_sha256


class EnrollForm(forms.Form):
    tenant_id = forms.CharField(widget=forms.HiddenInput(), initial='123e4567-e89b-12d3-a456-426614174000')
    system_id = forms.CharField(validators=[RegexValidator(r'[a-zA-Z]+', 'Enter a valid first name (only letters)')])
    os = forms.ChoiceField(choices=[('windows', 'Windows'), ('linux', 'Linux')])
    arch = forms.ChoiceField(choices=[('x86', 'x86'), ('x64', 'x64')])


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'tenant_id',
            'system_id',
            'os',
            'arch',
            Submit('submit', 'Submit', css_class='btn-success')
        )

class Enrollment():
    tenant_id = None
    node_system_id = None
    node = None

    def __init__(self, tenant_id, node_system_id):
        self.tenant_id = tenant_id
        self.node_system_id = node_system_id
        self.node = EnrolledNode.objects(tenant_id=self.tenant_id, node_system_id=self.node_system_id)

    def generate_node(self, node_os, node_arch):
        if self.node.exists():
            self.node = self.node[0]
            return self.node.node_secret
        else:
            m = hashlib.sha256()
            salt = os.urandom(32)
            secret = '{"node_system_id":{}, "tenant_id":{}, "secret":'.format(self.node_system_id, self.tenant_id) + self.generate_node_secret() + '}'
            encoded_secret = base64.b64encode(secret.encode())
            encoded_secret_string = encoded_secret.decode('utf-8')
            #print(type(encoded_secret))
            node_hash = pbkdf2_sha256.hash(encoded_secret_string)
            #print(host_hash.decode('ascii'))
            self.node = EnrolledNode(tenant_id=self.tenant_id, node_system_id=self.node_system_id, node_os=node_os, node_arch=node_arch, node_secret=encoded_secret_string, node_hash=node_hash)
            self.node.save()
            return encoded_secret_string

    def generate_node_secret(self):
        secret = secrets.token_hex(16)
        return secret

    def update_node_address(self, address):

        self.node.node_address = address
        self.node.save()

    def validate_enroll_secret(self, enroll_secret):
        decoded_secret = base64.b64decode(enroll_secret.encode())
        secret = json.loads(decoded_secret.decode())
        node = EnrolledNode.objects(tenant_id=secret['tenant_id'], node_system_id=secret['node_system_id'])
        if node:
            self.node = node[0]
        if not pbkdf2_sha256.verify(enroll_secret, self.node.node_hash):
            return None
        else:
            return self.node

    def validate_node(self, address, node_id, enroll_secret):

        node = EnrolledNode.objects(address=address, node_id=node_id)
        if node:
            self.node = node[0]

        if node and not pbkdf2_sha256.verify(enroll_secret, node.node_hash):
            return None
        else:
            return self.node


    def get_enrolled_nodes():

        return [row.address for row in EnrolledNode.objects.all()]