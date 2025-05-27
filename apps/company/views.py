from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import InviteCode, User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Organization
import secrets
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    print(f"Attempting to authenticate user: {username}")
    if user is not None:
        login(request, user)
        return Response({'message': 'Login successful'})
    else:
        return Response({'error': 'Invalid credentials'}, status=401)

@api_view(['GET'])
def join_organization(request):
    invite_code = request.data.get('invite_code')
    code = get_object_or_404(InviteCode, code=invite_code, is_used=False)
    request.user.organization = code.organization
    request.user.save()
    code.is_used = True
    code.save()
    return Response({'message': 'Joined organization successfully'})

@api_view(['GET'])
def get_users(request):
    users = User.objects.all().values('id', 'username', 'email')
    return Response({'users': list(users)})

@api_view(['POST'])
def create_organization(request):
    name = request.data.get('name')
    if not name:
        return Response({'error': 'Organization name is required'}, status=400)
    if Organization.objects.filter(name=name).exists():
        return Response({'error': 'Organization with this name already exists'}, status=400)
    organization = Organization.objects.create(name=name)
    request.user.organization = organization
    request.user.save()
    return Response({'message': 'Organization created successfully', 'organization_id': organization.id})

@api_view(['POST'])
def generate_invite_code(request):
    if not hasattr(request.user, 'organization') or request.user.organization is None:
        return Response({'error': 'User does not belong to any organization'}, status=400)
    code_str = secrets.token_urlsafe(8)
    invite_code = InviteCode.objects.create(
        code=code_str,
        organization=request.user.organization,
        is_used=False
    )
    return Response({'invite_code': invite_code.code})