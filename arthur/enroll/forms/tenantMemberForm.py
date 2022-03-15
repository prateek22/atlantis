from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.validators import RegexValidator

from ..models import Tenant


class TenantMemberForm(forms.Form):
    member_name = forms.CharField(validators=[RegexValidator(r'[a-zA-Z ]+', 'Enter a valid name (only letters)')])
    member_email = forms.CharField(validators=[RegexValidator(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", 'Enter a valid email')])
    member_password = forms.CharField(validators=[RegexValidator(r'[a-zA-Z]+', 'Enter a valid password (only letters)')])
    tenant = forms.ChoiceField(choices=[(tenant.tenant_name, tenant.tenant_name) for tenant in Tenant.objects().all()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'member_name',
            'member_email',
            'member_password',
            'tenant',
            Submit('submit', 'Submit', css_class='btn-success')
        )