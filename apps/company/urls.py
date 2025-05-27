# filepath: d:\Projects\Hypervisor-SimpliSmart\backend\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('join-organization/', views.join_organization, name='join_organization'),
    path('get-users/', views.get_users, name='get_users'),
    path('create-organization/', views.create_organization, name='create_organization'),
    path('generate-invite-code/', views.generate_invite_code, name='generate_invite_code'),
]