# Django imports
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# App imports
from ..enroll import Enrollment
from ..osqueryResponses import *
from ..settings import *
from ..alerts import *

#Miscellaneous imports
import json
from copy import deepcopy

@csrf_exempt
def distributed_read(request):

    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    address = request.META.get('REMOTE_ADDR')
    node_id = json_data.get('node_key')
    enroll_secret = json_data.get('enroll_secret')

    host = Enrollment(tenant_id=None, node_system_id=None)
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

    host = Enrollment(tenant_id=None, node_system_id=None)
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