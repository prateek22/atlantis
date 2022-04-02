# Django imports
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse, JsonResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# App imports
from ..enroll import Enrollment
from ..osqueryResponses import *
from ..forms.liveQueryForm import LiveQueryForm
from ..settings import *
from ..alerts import *
from enroll.models import *

#Miscellaneous imports
import json
import os
from copy import deepcopy

@csrf_exempt
def distributed_read(request):

    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    address = request.META.get('REMOTE_ADDR')
    node_id = json_data.get('node_key')
    enroll_secret = json_data.get('enroll_secret')

    #host = Enrollment()
    #node = host.validate_node(address, node_id, enroll_secret)
    #if not node:
    #    return JsonResponse(FAILED_ENROLL_RESPONSE)
        
    #exec_query = live_query.objects(query=query)
    #exec_query = DIST_QUERY[queries][id1]
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
        jsonstring = json.dumps(queries)
        jsonfile = open("results.json", "w")
        jsonfile.write(jsonstring)
        jsonfile.close()
        
    else:
        queries = []


    node_id = json_data.get('node_key')
    enroll_secret = json_data.get('enroll_secret')

    #host = Enrollment()
    #node = host.validate_node(address, node_id, enroll_secret)
    #if not node:
    #    return JsonResponse(FAILED_ENROLL_RESPONSE)

    #with open(LOG_OUTPUT_FILE, 'a') as f:
    #    for query in queries:
    #        if results[query] and len(results[query][0]):

    #            result_type = query.split('|')[0]
    #            direction = query.split('|')[1]
    #            uid = query.split('|')[2]

    #            if result_type == 'alert':
    #                print(results[query][0])
    #                update_elastic(direction, uid, results[query][0])
    #            else:
    #                for result in results[query]:
    #                    result['address'] = address
    #                    f.write(json.dumps(result) + '\n')

    return JsonResponse(EMPTY_RESPONSE)


def Dictionarize(query):
    """
    A utility function to convert object of type Results to a Python Dictionary
    """
    output = {}
    output["result_query"] = query.result_query
    output["node_keys"] = query.node_keys

    return output


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
        #query_results = dist_query_result.objects(result_query=result_query) #change from here change values to save to DB
        #if query_results:
        #    query_results = query_results[0]
        #else:
        #    raise HttpResponseBadRequest("Invalid details!!")
      #host_enroll = Enrollment(tenant_id=tenant_id, node_system_id=node_system_id)
      #secret = host_enroll.generate_node(node_arch=arch, node_os=os) # to here

 
   
   
   #op =  Results.objects.all()
   #returns = serialize("json", op, fields=('result_query', 'node_keys'))
   #return HttpResponse(returns, content_type="application/json")
   
   #query = models.Results.objects.first()
   # Multiple Blogs
   #queries = Results.objects.all()
   #tempqueries = []

   # Converting `QuerySet` to a Python Dictionary
   #query = Dictionarize(query)

   #for i in range(len(queries)):
   #    tempqueries.append(Dictionarize(queries[i])) # Converting `QuerySet` to a Python Dictionary

   #queries = tempqueries

   #data = {
       #"query": query,
       #"queries": queries
   #}

   #return JsonResponse(data)
   
   
@csrf_exempt
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
