from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.validators import RegexValidator

class EnrollForm(forms.Form):
    tenant_id = forms.CharField(widget=forms.HiddenInput())
    system_id = forms.CharField(validators=[RegexValidator(r'[a-zA-Z]+', 'Enter a valid first name (only letters)')])
    os = forms.ChoiceField(choices=[('windows', 'Windows'), ('linux', 'Linux')])
    arch = forms.ChoiceField(choices=[('x86', 'x86'), ('x64', 'x64')])


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'
        self.fields['tenant_id'] = forms.CharField(widget=forms.HiddenInput(), initial= self.args['tenant'].tenant_id)

        print(self.args)
        print(self.kwargs)

        self.helper.layout = Layout(
            'tenant_id',
            'system_id',
            'os',
            'arch',
            Submit('submit', 'Submit', css_class='btn-success')
        )