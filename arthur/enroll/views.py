from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from .models import Tenant
from .enroll import EnrollForm, Enrollment
import zipfile, mimetypes, os


class TenantListView(ListView):
    model = Tenant



