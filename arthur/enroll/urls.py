from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .views.stats_views import TenantMemberListView, TenantListView

from . import views

app_name = 'edr'

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('enroll', views.enroll, name='enroll'),
    path('config', views.config, name='config'),
    path('logger', views.logger, name='logger'),
    path('distributed_read', views.distributed_read, name='distributed_read'),
    path('distributed_write', views.distributed_write, name='distributed_write'),
    path('distributed_query', views.distributed_query, name='distributed_query'),
    path('distributed_results', views.distributed_results, name='distributed_results'),
    path('alert', views.alert, name='alert'),
    path('tenantList', TenantListView.as_view(), name='tenantList'),
    path('members', TenantMemberListView.as_view(), name='members'),
    path('addTenant', views.addTenant, name='addTenant'),
    path('addTenantMember', views.addTenantMember, name='addTenantMember'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('registerUser', views.RegisterView.as_view(), name='register'),
    path('hello', views.HelloView.as_view(), name='hello'),
    path('home', views.HelloView.as_view(), name='home'),
    path('token', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register', views.RegisterNodeView.as_view(), name='api_register'),
    path('api/node_list', views.NodeList.as_view(), name='api_node_list'),
]