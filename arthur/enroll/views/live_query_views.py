# Django imports
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# App imports
from ..enroll import Enrollment
from ..osqueryResponses import *
from ..settings import *
from ..alerts import *
from ..forms.liveQueryForm import LiveQueryForm

#Miscellaneous imports
import json
from copy import deepcopy

@csrf_exempt
def distributed_read(request):

    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    address = request.META.get('REMOTE_ADDR')
    node_id = json_data.get('node_key')

    host = Enrollment(tenant_id=None, node_system_id=None)
    node = host.validate_node(address, node_id)
    if not node:
        return JsonResponse(FAILED_ENROLL_RESPONSE)

    query = deepcopy(DIST_QUERY)
    #query = check_alerts(address, query)

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
        print(queries)
        print("\n")
        print(results)
        jsonstring = json.dumps(queries)
        jsonfile = open("../results.json", "w")
        jsonfile.write(jsonstring)
        jsonfile.close()
    
    else:
        queries = []

    node_id = json_data.get('node_key')

    host = Enrollment(tenant_id=None, node_system_id=None)
    node = host.validate_node(address, node_id)
    if not node:
        return JsonResponse(FAILED_ENROLL_RESPONSE)

    #with open(LOG_OUTPUT_FILE, 'a') as f:
    #    for query in queries:
    #        if results[query] and len(results[query][0]):

    #            result_type = query.split('|')[0]
    #            direction = query.split('|')[1]
    #            uid = query.split('|')[2]

    #           if result_type == 'alert':
    #                print(results[query][0])
    #                update_elastic(direction, uid, results[query][0])
    #            else:
    #                for result in results[query]:
    #                    result['address'] = address
    #                    f.write(json.dumps(result) + '\n')

    return JsonResponse(EMPTY_RESPONSE)

@csrf_exempt
def distributed_query(request):
  
  if request.method == 'GET':
        form = LiveQueryForm()
        return render(request, 'enroll/results.html', {'form': form})  
  elif request.method == 'POST':
        #raise HttpResponseBadRequest("Invalid details!!")
        form = LiveQueryForm(request.POST)
        if form.is_valid():
            results = live_query()
            results.query = form.cleaned_data['user_query']
            #results.tags = form.cleaned_data['tags']
            #results.node_keys = form.cleaned_data['node_keys']
            print(result.query)
            DIST_QUERY[queries][id1] = result.query
            results.save()
        html = "<html><body>POST request successful.</body></html>"
        return HttpResponse(html)

def distributed_results(request):
    with open("/root/PrateekPro/atlantis/arthur/enroll/result.json") as file:
      data = json.load(file)
      return JsonResponse(data)
    #data = request.body.decode('utf-8')
    #json_data = json.loads(data)
    #query = json_data.get('query')
    #tags = json_data.get('tags')
    #add tag here
    
   #if not validate_node_key(address, node_key):
   #   return JsonResponse(FAILED_ENROLL_RESPONSE)
      
    #live_query = live_query(query=query, tags=tags)
    #live_query.save()
    
    return JsonResponse(EMPTY_RESPONSE)