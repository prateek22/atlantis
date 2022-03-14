from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Tenant
from .enroll import EnrollForm, Enrollment
import zipfile, mimetypes, os

def index(request):
    return render(request, 'enroll/index.html')

def enroll(request):
    if request.method == 'GET':
        form = EnrollForm()
        return render(request, 'enroll/enroll.html', {'form': form})
    elif request.method == 'POST':
        form = EnrollForm(request.POST)
        if form.is_valid():
            tenant_id = form.cleaned_data['tenant_id']
            host_system_id = form.cleaned_data['host_system_id']
            os = form.cleaned_data['os']
            arch = form.cleaned_data['arch']
        tenant = Tenant.objects(tenant_id=tenant_id)
        if tenant:
            tenant = tenant[0]
        else:
            raise HttpResponseBadRequest("Invalid details!!")
        host_enroll = Enrollment(tenant_id=tenant_id, host_system_id=host_system_id)
        secret = host_enroll.generate_host(host_arch=arch, host_os=os)
        with open(tenant.tenant_name+'_'+host_system_id+'.secret', 'x') as f:
            f.write(secret)
        osquery_flag_string = """--tls_hostname="""+tenant.tenant_domain+""".edr.api:8000
                --tls_server_certs=/root/Capstone_project/EDR/capstone/certs/ca.pem
                --enroll_secret_path=/root/Capstone_project/EDR/capstone/"""+tenant.tenant_name+'_'+host_system_id+""".secret
                --enroll_tls_endpoint=/osquery/enroll
                --host_identifier=uuid
                --distributed_tls_read_endpoint=/osquery/distributed_read
                --distributed_tls_write_endpoint=/osquery/distributed_write
                --disable_distributed=false
                --distributed_interval=5
                --distributed_plugin=tls

                --config_plugin=tls
                #--config_refresh=5
                --config_tls_endpoint=/osquery/config
                --logger_plugin=tls
                --logger_tls_endpoint=/osquery/logger"""
        with open(tenant.tenant_name+'_'+host_system_id+'.flags', 'x') as f:
            f.write(osquery_flag_string)
        zf = zipfile.ZipFile(tenant.tenant_name+'_'+host_system_id+".zip", 'x')
        zf.write(tenant.tenant_name+'_'+host_system_id+'.secret')
        zf.write(tenant.tenant_name+'_'+host_system_id+'.flags')
        zf.close()
        zip_file = open(tenant.tenant_name+'_'+host_system_id+".zip", 'rb')
        return FileResponse(zip_file)
        #return HttpResponse('Generated Secret: ' + secret)

