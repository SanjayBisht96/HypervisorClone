from django.db import models
from  apps.cluster.models import Cluster

class Deployment(models.Model):
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name='deployments')
    docker_image = models.CharField(max_length=255)
    ram_required = models.IntegerField()
    cpu_required = models.IntegerField()
    gpu_required = models.IntegerField()
    priority = models.IntegerField(default=0)  # Higher value = higher priority
    status = models.CharField(max_length=50, default='queued')  # queued, running, completed
    created_at = models.DateTimeField(auto_now_add=True)