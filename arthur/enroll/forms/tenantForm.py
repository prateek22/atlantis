from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.validators import RegexValidator


class TenantForm(forms.Form):
    tenant_name = forms.CharField(validators=[RegexValidator(r'[a-zA-Z]+', 'Enter a valid tenant name (only letters)')])
    tenant_domain = forms.CharField(validators=[RegexValidator(r'[a-zA-Z]+', 'Enter a valid tenant domain (only letters)')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'tenant_name',
            'tenant_domain',
            Submit('submit', 'Submit', css_class='btn-success')
        )