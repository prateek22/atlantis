from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.validators import RegexValidator

from ..models import live_query, EnrolledNode

class EnrollForm(forms.Form):
    node_id = forms.ChoiceField(choices=[(node.node_id, node.node_system_id) for node in EnrolledNode.objects(tenant_id='123e4567-e89b-12d3-a456-426614174000')])
    query_id = forms.ChoiceField(choices=[(query.query_id, query.query) for query in live_query.objects().all()])
    user_query = forms.CharField(validators=[RegexValidator(r'[a-zA-Z*,_]+', 'Enter a valid query (only letters and *,_)')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'node_id',
            'query_id',
            'user_query',
            Submit('submit', 'Submit', css_class='btn-success')
        )