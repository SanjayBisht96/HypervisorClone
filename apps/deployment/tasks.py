from celery import shared_task
from .models import Deployment
from apps.cluster.models import Cluster
import docker
from collections import defaultdict
import datetime

@shared_task
def deployment_scheduler():

    # Define priority levels (e.g., 3: high, 2: medium, 1: low)
    PRIORITY_LEVELS = [3, 2, 1]
    AGING_THRESHOLD = datetime.timedelta(hours=1)  # Example: 1 hour

    # Fetch all queued deployments
    now = datetime.datetime.now(datetime.timezone.utc)
    queued_deployments = Deployment.objects.filter(status='queued')

    # Group deployments by priority
    priority_queues = defaultdict(list)
    for dep in queued_deployments:
        # Aging: promote priority if waiting too long
        wait_time = now - dep.created_at
        effective_priority = dep.priority
        # Aging: promote priority if waiting too long
        if wait_time > AGING_THRESHOLD and dep.priority < max(PRIORITY_LEVELS):
            effective_priority = dep.priority + 1  # Promote priority

        # Check if any cluster has enough resources for this deployment
        has_space = False
        for cluster in Cluster.objects.all():
            if (cluster.ram >= dep.ram_required and
            cluster.cpu >= dep.cpu_required and
            cluster.gpu >= dep.gpu_required):
                has_space = True
                break
        if not has_space:
            # Lower the effective priority if no cluster can currently fit this deployment
            effective_priority = min(effective_priority, min(PRIORITY_LEVELS))
        priority_queues[effective_priority].append(dep)

    # Process queues from highest to lowest priority
    for priority in sorted(priority_queues.keys(), reverse=True):
        # Sort each queue by created_at (FIFO within priority)
        queue = sorted(priority_queues[priority], key=lambda d: d.created_at)
        # Bin packing: try to fit as many deployments as possible concurrently
        clusters = {c.id: c for c in Cluster.objects.all()}
        scheduled = set()
        while queue:
            for dep in list(queue):
                cluster = clusters[dep.cluster_id]
                if (cluster.ram >= dep.ram_required and
                    cluster.cpu >= dep.cpu_required and
                    cluster.gpu >= dep.gpu_required):
                    # Allocate resources
                    cluster.ram -= dep.ram_required
                    cluster.cpu -= dep.cpu_required
                    cluster.gpu -= dep.gpu_required
                    cluster.save()
                    run_deployment.delay(dep.id)
                    scheduled.add(dep.id)
                    queue.remove(dep)
            # If no deployments were scheduled in this pass, break to avoid infinite loop
            if not scheduled:
                break
            scheduled.clear()

@shared_task
def run_deployment(deployment_id):
    deployment = Deployment.objects.get(id=deployment_id)
    cluster = deployment.cluster

    try:
        # Run Docker container
        client = docker.from_env()
        container = client.containers.run(
            deployment.docker_image,
            detach=True
        )

        # Update deployment status
        deployment.status = 'running'
        deployment.save()

        # Wait for the container to complete
        container.wait()
        deployment.status = 'completed'
        deployment.save()

        # Release resources
        cluster.ram += deployment.ram_required
        cluster.cpu += deployment.cpu_required
        cluster.gpu += deployment.gpu_required
        cluster.save()

    except Exception as e:
        # Handle errors and mark deployment as failed
        deployment.status = 'failed'
        deployment.save()
        print(f"Error during deployment {deployment.id}: {e}")