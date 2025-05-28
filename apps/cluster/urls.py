# filepath: d:\Projects\Hypervisor-SimpliSmart\hypervisor\apps\company\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-cluster/', views.create_cluster, name='create_cluster'),
    path('get-cluster-resources/<int:cluster_id>/', views.get_cluster_resources, name='get_cluster_resources'),
]