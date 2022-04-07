from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import RegistrationSerializer, LoginSerializer
from ..renderers import TenantMemberJSONRenderer
from ..models import Tenant
from ..utils import hostname_from_request

class LoginView(TemplateView, View):
    template_name = 'enroll/login.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

class LoginView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (TenantMemberJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't  have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        tenant = Tenant.objects(tenant_domain=hostname_from_request(request))
        if tenant:
            tenant = tenant[0]
        else:
            return HttpResponseBadRequest("{'user':{'message':'Invalid details!!'}}")
        user['tenant_id'] = tenant.tenant_id
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('home')

        logout(request)
        messages.success(request, "You are now logged out!")
        return redirect('home')

class RegisterView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (TenantMemberJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MembersView(LoginRequiredMixin, TemplateView, View):
    template_name = 'enroll/members_only.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})