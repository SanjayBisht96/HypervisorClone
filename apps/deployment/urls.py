from django.urls import path
from . import views

urlpatterns = [
    path('create-deployment/', views.create_deployment_view, name='create_deployment'),
]