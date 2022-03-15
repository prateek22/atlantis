# Django imports
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# App imports
from ..models import Tenant
from ..enroll import EnrollForm, Enrollment
from ..osqueryResponses import *
from ..settings import *
from ..alerts import *

#Miscellaneous imports
import zipfile, json
from copy import deepcopy

def index(request):
    return render(request, 'enroll/index.html')

# Endpoint for registering new nodes
def register(request):
    if request.method == 'GET':
        form = EnrollForm()
        return render(request, 'enroll/enroll.html', {'form': form})
    elif request.method == 'POST':
        form = EnrollForm(request.POST)
        if form.is_valid():
            tenant_id = form.cleaned_data['tenant_id']
            node_system_id = form.cleaned_data['system_id']
            os = form.cleaned_data['os']
            arch = form.cleaned_data['arch']
        tenant = Tenant.objects(tenant_id=tenant_id)
        if tenant:
            tenant = tenant[0]
        else:
            raise HttpResponseBadRequest("Invalid details!!")
        host_enroll = Enrollment(tenant_id=tenant_id, node_system_id=node_system_id)
        secret = host_enroll.generate_node(node_arch=arch, node_os=os)
        with open(tenant.tenant_name+'_'+node_system_id+'.secret', 'x') as f:
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
        with open(tenant.tenant_name+'_'+node_system_id+'.flags', 'x') as f:
            f.write(osquery_flag_string)
        zf = zipfile.ZipFile(tenant.tenant_name+'_'+node_system_id+".zip", 'x')
        zf.write(tenant.tenant_name+'_'+node_system_id+'.secret')
        zf.write(tenant.tenant_name+'_'+node_system_id+'.flags')
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
        enroll_secret = json_data.get('enroll_secret')
        address = request.META.get('REMOTE_ADDR')
        host = Enrollment()
        node = host.validate_enroll_secret(enroll_secret)
        if not enroll_secret or not node:
            return JsonResponse(FAILED_ENROLL_RESPONSE)
        
        node_key = host.update_node_address(address)
        response = ENROLL_RESPONSE
        response['node_key'] = node_key

        return JsonResponse(response)


@csrf_exempt
def config(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        address = request.META.get('REMOTE_ADDR')
        node_id = json_data.get('node_key')
        enroll_secret = json_data.get('enroll_secret')

        host = Enrollment()
        node = host.validate_node(address, node_id, enroll_secret)
        if not node:
            return JsonResponse(FAILED_ENROLL_RESPONSE)

        return JsonResponse(TEST_SCHED_QUERY)


@csrf_exempt
def logger(request):

    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    address = request.META.get('REMOTE_ADDR')
    results = json_data.get('data')
    log_type = json_data.get('log_type')
    node_id = json_data.get('node_key')
    enroll_secret = json_data.get('enroll_secret')

    host = Enrollment()
    node = host.validate_node(address, node_id, enroll_secret)
    if not node:
        return JsonResponse(FAILED_ENROLL_RESPONSE)

    if results and log_type == 'result':
        with open(LOG_OUTPUT_FILE, 'a') as f:
            for result in results:
                logs = result['snapshot']
                for log in logs:
                    log['address'] = address
                    f.write(json.dumps(log) + '\n')

    return JsonResponse(EMPTY_RESPONSE)


@csrf_exempt
def distributed_read(request):

    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    address = request.META.get('REMOTE_ADDR')
    node_id = json_data.get('node_key')
    enroll_secret = json_data.get('enroll_secret')

    host = Enrollment()
    node = host.validate_node(address, node_id, enroll_secret)
    if not node:
        return JsonResponse(FAILED_ENROLL_RESPONSE)

    query = deepcopy(DIST_QUERY)
    query = check_alerts(address, query)

    if not len(query['queries']):
        return JsonResponse(EMPTY_RESPONSE)

    return JsonResponse(query)

@csrf_exempt
def distributed_write(request):

    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    address = request.META.get('REMOTE_ADDR')
    results = json_data.get('queries')
    if results:
        queries = results.keys()
    else:
        queries = []


    node_id = json_data.get('node_key')
    enroll_secret = json_data.get('enroll_secret')

    host = Enrollment()
    node = host.validate_node(address, node_id, enroll_secret)
    if not node:
        return JsonResponse(FAILED_ENROLL_RESPONSE)

    with open(LOG_OUTPUT_FILE, 'a') as f:
        for query in queries:
            if results[query] and len(results[query][0]):

                result_type = query.split('|')[0]
                direction = query.split('|')[1]
                uid = query.split('|')[2]

                if result_type == 'alert':
                    print(results[query][0])
                    update_elastic(direction, uid, results[query][0])
                else:
                    for result in results[query]:
                        result['address'] = address
                        f.write(json.dumps(result) + '\n')

    return JsonResponse(EMPTY_RESPONSE)