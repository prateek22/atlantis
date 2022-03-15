from django.urls import path

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
    path('alert', views.alert, name='alert'),
    path('tenantList', TenantListView.as_view(), name='tenantList'),
    path('tenantMemberList', TenantMemberListView.as_view(), name='tenantMemberList'),
    path('addTenant', views.addTenant, name='addTenant'),
    path('addTenantMember', views.addTenantMember, name='addTenantMember'),
]