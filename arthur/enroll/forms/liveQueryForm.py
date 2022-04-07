from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.validators import RegexValidator

from ..models import live_query, EnrolledNode, dist_query_result

class LiveQueryForm(forms.Form):
    #node_id = forms.ChoiceField(choices=[(node.node_id, node.node_system_id) for node in EnrolledNode.objects(tenant_id='123e4567-e89b-12d3-a456-426614174000')])
    #tags = forms.CharField(validators=[RegexValidator(r'[a-zA-Z*,_]+', 'Enter a valid query (only letters and *,_)')])
    user_query = forms.CharField(validators=[RegexValidator(r'[a-zA-Z*,_; ]+', 'Enter a valid query (only letters and *,_)')])
    qid = forms.CharField(validators=[RegexValidator(r'[a-zA-Z*,_; ]+', 'Enter a valid query (only letters and *,_)')])
    #query_results = forms.ChoiceField(choices=[(qresults.result_query, qresults.node_keys) for qresults in dist_query_result().all()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
     #       'node_id',
            'qid',
            'user_query',
     #       'query_results',
            Submit('submit', 'Submit', css_class='btn-success')
        )
