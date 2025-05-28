from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Deployment, Cluster
from .tasks import create_deployment

@api_view(['POST'])
def create_deployment_view(request):
    cluster_id = request.data.get('cluster_id')
    docker_image = request.data.get('docker_image')
    ram_required = request.data.get('ram_required')
    cpu_required = request.data.get('cpu_required')
    gpu_required = request.data.get('gpu_required')
    priority = request.data.get('priority', 0)

    cluster = Cluster.objects.get(id=cluster_id)
    deployment = Deployment.objects.create(
        cluster=cluster,
        docker_image=docker_image,
        ram_required=ram_required,
        cpu_required=cpu_required,
        gpu_required=gpu_required,
        priority=priority,
        status='queued'
    )

    # Trigger Celery task
    create_deployment.delay(deployment.id)

    return Response({'message': 'Deployment created and queued', 'deployment_id': deployment.id})