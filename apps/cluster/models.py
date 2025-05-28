from django.db import models

# Create your models here.
class Cluster(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ram = models.IntegerField()  # RAM in MB
    cpu = models.IntegerField()  # Number of CPUs
    gpu = models.IntegerField()  # Number of GPUs
    created_at = models.DateTimeField(auto_now_add=True)

class Resource(models.Model):
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name='resources')
    allocated_ram = models.IntegerField(default=0)  # Allocated RAM in MB
    allocated_cpu = models.IntegerField(default=0)  # Allocated CPUs
    allocated_gpu = models.IntegerField(default=0)  # Allocated GPUs
