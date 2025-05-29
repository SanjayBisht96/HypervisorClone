from celery import shared_task
from .models import Deployment
from apps.cluster.models import Cluster
import docker
from collections import defaultdict
import datetime
import logging
import sys
from django.db import transaction

logger = logging.getLogger(__name__)

@shared_task
def deployment_scheduler():
    logger.info("Starting deployment scheduler...")
    
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
        failed = set()
        try:
            while queue:
                for dep in list(queue):
                    cluster = clusters[dep.cluster_id]
                    if (cluster.ram >= dep.ram_required and
                        cluster.cpu >= dep.cpu_required and
                        cluster.gpu >= dep.gpu_required):
                        run_deployment(dep.id)
                        scheduled.add(dep.id)
                    else:
                        failed.add(dep.id)
                    queue.remove(dep)
        except Exception as e:
            logger.error(f"Error during deployment scheduling: {e}")
            sys.stdout.flush()
        if failed:
            logger.warning(f"Failed to schedule {len(failed)} deployments due to insufficient resources.")

@transaction.atomic
@shared_task
def run_deployment(deployment_id):
    deployment = Deployment.objects.get(id=deployment_id)
    cluster = deployment.cluster
    logger.info("Creating image...")
    try:
        # Run Docker container
        logger.info("call docker:",)
        client = docker.from_env()
        logger.info("Deployment ID:", deployment.id)
        logger.info("Docker Image:", deployment.docker_image)
        container = client.containers.run(
            deployment.docker_image,
            detach=True
        )
        logger.info("Container ID:", container.short_id)
        # Update deployment status
        deployment.status = 'running'
        deployment.save()

        # Wait for the container to complete
        # Poll until container status is 'running' or timeout after N seconds
        timeout = 30  # seconds
        interval = 1  # second
        elapsed = 0

        while elapsed < timeout:
            container.reload()  # refresh container info
            if container.status == 'running':
                deployment.status = 'completed'
                deployment.save()
                # Allocate resources
                cluster.ram -= deployment.ram_required
                cluster.cpu -= deployment.cpu_required
                cluster.gpu -= deployment.gpu_required
                cluster.save()
                logger.info("Successfully created image...")
                break
            elif container.status in ('exited', 'dead'):
                logger.info(f"Container {container.short_id} failed to start. Status: {container.status}")
                deployment.status = 'failed'
                deployment.save()
                logger.info("Failed to create image...")
                break
            datetime.time.sleep(interval)
            elapsed += interval

    except Exception as e:
        # Handle errors and mark deployment as failed
        deployment.status = 'failed'
        deployment.save()
        logger.error(f"Error during deployment {deployment.id}: {e}")


@shared_task
def cleanup_completed_deployments():
    completed_deployments = Deployment.objects.filter(status='completed')
    client = docker.from_env()
    for deployment in completed_deployments:
        try:
            # Find and remove the container by image (or use a container name/id if available)
            containers = client.containers.list(all=True, filters={"ancestor": deployment.docker_image})
            for container in containers:
                container.remove(force=True)
            # Optionally, update deployment status or delete the deployment
            # deployment.delete()
        except Exception as e:
            print(f"Error removing container for deployment {deployment.id}: {e}")