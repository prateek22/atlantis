from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.validators import RegexValidator
from .models import Host
import secrets, hashlib, base64, os, binascii

# class NameWidget(forms.MultiWidget):

#     def __init__(self, attrs=None):
#         super().__init__([
#             forms.TextInput()
#         ], attrs)

#     def decompress(self, value):
#         if value:
#             return value.split(' ')
#         return ['', '']

# class NameField(forms.MultiValueField):

#     widget = NameWidget

#     def __init__(self, *args, **kwargs):

#         fields = (
#             forms.CharField(validators=[
#                 RegexValidator(r'[a-zA-Z]+', 'Enter a valid first name (only letters)')
#             ]),
#         )

#         super().__init__(fields, *args, **kwargs)

#     def compress(self, data_list):
#         return f'{data_list[0]} {data_list[1]}'


class EnrollForm(forms.Form):
    tenant_id = forms.CharField(widget=forms.HiddenInput(), initial='123e4567-e89b-12d3-a456-426614174000')
    host_system_id = forms.CharField(validators=[RegexValidator(r'[a-zA-Z]+', 'Enter a valid first name (only letters)')])
    os = forms.ChoiceField(choices=[('windows', 'Windows'), ('linux', 'Linux')])
    arch = forms.ChoiceField(choices=[('x86', 'x86'), ('x64', 'x64')])


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'tenant_id',
            'host_system_id',
            'os',
            'arch',
            Submit('submit', 'Submit', css_class='btn-success')
        )

class Enrollment():
    tenant_id = None
    host_system_id = None
    host = None

    def __init__(self, tenant_id, host_system_id):
        self.tenant_id = tenant_id
        self.host_system_id = host_system_id
        self.host = Host.objects(tenant_id=self.tenant_id, host_system_id=self.host_system_id)
        if self.host:
            self.host = self.host[0]

    def generate_host(self, host_os, host_arch):
        if self.host != None:
            return self.host.host_secret
        else:
            m = hashlib.sha256()
            salt = os.urandom(32)
            secret = "host_system_id={}, tenant_id={}, secret=".format(self.host_system_id, self.tenant_id) + self.generate_host_secret()
            encoded_secret = base64.b64encode(secret.encode())
            encoded_secret_string = encoded_secret.decode('utf-8')
            print(type(encoded_secret))
            host_hash = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', encoded_secret, salt, 10000)).decode()
            #print(host_hash.decode('ascii'))
            self.host = Host(tenant_id=self.tenant_id, host_system_id=self.host_system_id, host_os=host_os, host_arch=host_arch, host_secret=encoded_secret_string, host_hash=host_hash)
            self.host.save()
            return encoded_secret_string

    def generate_host_secret(self):
        secret = secrets.token_hex(16)
        return secret