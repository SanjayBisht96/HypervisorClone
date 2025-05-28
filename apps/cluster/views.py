from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cluster, Resource

# Create your views here.

@api_view(['POST'])
def create_cluster(request):
    name = request.data.get('name')
    ram = request.data.get('ram')
    cpu = request.data.get('cpu')
    gpu = request.data.get('gpu')

    if not all([name, ram, cpu, gpu]):
        return Response({'error': 'All fields are required'}, status=400)

    cluster = Cluster.objects.create(name=name, ram=ram, cpu=cpu, gpu=gpu)
    Resource.objects.create(cluster=cluster)
    return Response({'message': 'Cluster created successfully', 'cluster_id': cluster.id})

@api_view(['GET'])
def get_cluster_resources(request, cluster_id):
    try:
        cluster = Cluster.objects.get(id=cluster_id)
        resources = cluster.resources.first()
        return Response({
            'cluster': cluster.name,
            'total_ram': cluster.ram,
            'total_cpu': cluster.cpu,
            'total_gpu': cluster.gpu,
            'allocated_ram': resources.allocated_ram,
            'allocated_cpu': resources.allocated_cpu,
            'allocated_gpu': resources.allocated_gpu,
        })
    except Cluster.DoesNotExist:
        return Response({'error': 'Cluster not found'}, status=404)

@api_view(['DELETE'])
def delete_cluster(request, cluster_id):
    try:
            cluster = Cluster.objects.get(id=cluster_id)
            cluster.delete()
            return Response({'message': 'Cluster deleted successfully'})
    except Cluster.DoesNotExist:
        return Response({'error': 'Cluster not found'}, status=404)
