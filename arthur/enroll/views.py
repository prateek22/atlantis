from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return HttpResponse("Hello, world. You're at the enroll welcome.")

@csrf_exempt
def enroll(request):
    if request.method == 'GET':
        return HttpResponse("GET /enroll.")
    elif request.method == 'POST':
        return HttpResponse("POST /enroll.")