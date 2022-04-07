from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView, View

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import RegistrationSerializer

from ..forms.tenantMemberForm import TenantMemberForm

class LoginView(TemplateView, View):
    template_name = 'enroll/login.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None:
            # the password verified for the user
            if user.is_active:
                login(request, user)
                messages.success(request, "You are now logged in!")
            else:
                messages.warning(request, "The password is valid, but the account has been disabled!")
        else:
            # the authentication system was unable to verify the username and password
            messages.warning(request, "The username and password were incorrect.")

        return redirect('edr:home')#redirect(request.POST.get('next', 'home'))


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