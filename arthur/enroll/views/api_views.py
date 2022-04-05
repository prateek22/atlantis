from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # <-- Here
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse, JsonResponse
from django.core import serializers

# App imports
from ..models import Tenant
from ..forms.enrollForm import EnrollForm
from ..models import EnrolledNode
from ..utils import hostname_from_request
from ..enroll import Enrollment

import json, zipfile

class HelloView(APIView):
    permission_classes = (IsAuthenticated,)             # <-- And here

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

class RegisterNodeView(APIView):
    def post(self,request):
        tenant = Tenant.objects(tenant_domain=hostname_from_request(request))
        if tenant:
            tenant = tenant[0]
        else:
            return HttpResponseBadRequest("Invalid details!!")
        form = EnrollForm(tenant, request.POST)
        if form.is_valid():
            tenant_id = form.cleaned_data['tenant_id']
            node_system_id = form.cleaned_data['system_id']
            os = form.cleaned_data['os']
            arch = form.cleaned_data['arch']
        #Tenant.__keyspace__ = "db"
        tenant = Tenant.objects(tenant_id=tenant_id)
        if tenant:
            tenant = tenant[0]
        else:
            return HttpResponseBadRequest("Invalid details!!")
        try:
            host_enroll = Enrollment(tenant_id=tenant_id, node_system_id=node_system_id)
        except Exception:
            return HttpResponseBadRequest("Invalid details!!")
        secret = host_enroll.generate_node(node_arch=arch, node_os=os)
        with open(tenant.tenant_name+'_'+node_system_id+'.secret', 'x') as f:
            f.write(secret)
        osquery_flag_string = """--tls_hostname="""+tenant.tenant_domain+""".edr.api:8000
                --tls_server_certs=./certs/ca.pem
                --enroll_secret_path=../"""+tenant.tenant_name+'_'+node_system_id+""".secret
                --enroll_tls_endpoint=/enroll/enroll
                --host_identifier=uuid
                --distributed_tls_read_endpoint=/enroll/distributed_read
                --distributed_tls_write_endpoint=/enroll/distributed_write
                --disable_distributed=false
                --distributed_interval=5
                --distributed_plugin=tls

                --config_plugin=tls
                #--config_refresh=5
                --config_tls_endpoint=/enroll/config
                --logger_plugin=tls
                --logger_tls_endpoint=/enroll/logger"""
        with open(tenant.tenant_name+'_'+node_system_id+'.flags', 'x') as f:
            f.write(osquery_flag_string)
        zf = zipfile.ZipFile(tenant.tenant_name+'_'+node_system_id+".zip", 'x')
        zf.write(tenant.tenant_name+'_'+node_system_id+'.secret')
        zf.write(tenant.tenant_name+'_'+node_system_id+'.flags')
        zf.close()
        zip_file = open(tenant.tenant_name+'_'+node_system_id+".zip", 'rb')
        return FileResponse(zip_file)
        #return HttpResponse('Generated Secret: ' + secret)

class LiveQueryView(APIView):
    pass

class LogsView(APIView):
    pass

class RegisterMultipleNodes(APIView):
    permission_classes = (IsAuthenticated,)             # <-- And here

    def post(self, request):
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        print(json_data)
        for deserialized_object in serializers.deserialize("jsonl", data):
            if self.object_should_be_saved(deserialized_object):
                deserialized_object.save()
        content = {'message': 'Hello, World!'}
        return Response(content)

    def object_should_be_saved(node):
        existing_node = EnrolledNode.objects(node_system_id=node.node_system_id, tenant_id=node.tenant_id)
        if existing_node:
            return False
        else:
            return True

