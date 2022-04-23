# Django imports
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse, JsonResponse
from django.shortcuts import render
from django import forms
from django.views.decorators.csrf import csrf_exempt

from .kafka_views import kfk

# App imports
from ..models import Logs, Tenant, alerts
from ..forms.enrollForm import EnrollForm
from ..enroll import Enrollment
from ..osqueryResponses import *
from ..settings import *
from ..alerts import *
from ..utils import hostname_from_request

#Miscellaneous imports
import zipfile, json
from copy import deepcopy

def index(request):
    return render(request, 'enroll/index.html')

# Endpoint for registering new nodes
def register(request):
    if request.method == 'GET':
        tenant = Tenant.objects(tenant_domain=hostname_from_request(request))
        if tenant:
            tenant = tenant[0]
        else:
            return HttpResponseBadRequest("Invalid details!!")
        form = EnrollForm(tenant)
        return render(request, 'enroll/enroll.html', {'form': form})
    elif request.method == 'POST':
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
                --tls_server_certs=./ca.pem
                --enroll_secret_path=./"""+tenant.tenant_name+'_'+node_system_id+""".secret
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
        zf.write('ca.pem')
        zf.close()
        zip_file = open(tenant.tenant_name+'_'+node_system_id+".zip", 'rb')
        return FileResponse(zip_file)
        #return HttpResponse('Generated Secret: ' + secret)

@csrf_exempt
def enroll(request):
    if request.method == 'GET':
        return JsonResponse(FAILED_ENROLL_RESPONSE)
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        print(json_data)
        enroll_secret = json_data.get('enroll_secret')
        host = Enrollment(tenant_id=None, node_system_id=None)
        try:
            node = host.validate_enroll_secret(enroll_secret)
            if not enroll_secret or not node:
                return JsonResponse(FAILED_ENROLL_RESPONSE)
        except Exception:
            return JsonResponse(FAILED_ENROLL_RESPONSE)
        
        node_key = host.update_node_info(data)
        response = ENROLL_RESPONSE
        response['node_key'] = node_key
        print(node_key.int)
        print(node_key.node)

        return JsonResponse(response)


@csrf_exempt
def config(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        print(json_data)
        address = request.META.get('REMOTE_ADDR')
        node_id = json_data.get('node_key')

        host = Enrollment(tenant_id=None, node_system_id=None)
        node = host.validate_node(node_id)
        if not node:
            return JsonResponse(FAILED_ENROLL_RESPONSE)

        return JsonResponse(TEST_SCHED_QUERY)


@csrf_exempt
def logger(request):

    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    print(json_data)
    address = request.META.get('REMOTE_ADDR')
    logs = json_data.get('data')
    log_type = json_data.get('log_type')
    node_id = json_data.get('node_key')

    host = Enrollment(tenant_id=None, node_system_id=None)
    node = host.validate_node(node_id)
    if not node:
        return JsonResponse(FAILED_ENROLL_RESPONSE)

    if logs and log_type == 'result':
        #kfk(results)
        for log in logs:
            print(log['name'])
            print(log['action'])
            print(log['calendarTime'])
            print(json.dumps(log['columns']))
            new_log = Logs(node_id=node_id, log_type=log['name'], log_data=json.dumps(log['columns']), log_ts=log['calendarTime'], log_action=log['action'])
            new_log.save()
    return JsonResponse({'msg': 'Saved the logs!!'})
    #return JsonResponse(EMPTY_RESPONSE)

@csrf_exempt
def alert(request):

    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    src_ip = json_data.get('src_ip')
    src_port = json_data.get('src_port')
    dest_ip = json_data.get('dest_ip')
    dest_port = json_data.get('dest_port')
    uid = json_data.get('alert_uid')
    secret = json_data.get('secret')
    host = Enrollment(tenant_id=None, node_system_id=None)
    enrolled_nodes = host.get_enrolled_nodes()

    if not secret == LOGSTASH_SECRET or \
            (not src_ip in enrolled_nodes and not dest_ip in enrolled_nodes):
        return None

    alerts.objects.all().delete()

    alert = alerts(src_ip=src_ip, src_port=src_port, dest_ip=dest_ip, dest_port=dest_port, uid=uid)
    alert.save()

    print(alerts.objects.all())

    return JsonResponse(EMPTY_RESPONSE)


