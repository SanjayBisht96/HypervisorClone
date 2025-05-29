import pytest
from apps.cluster.models import Cluster
from apps.deployment.models import Deployment
from apps.deployment.tasks import deployment_scheduler, cleanup_completed_deployments
from django.utils.timezone import now
from django.conf import settings

def test_sanity():
    assert settings.CELERY_TASK_ALWAYS_EAGER is True

@pytest.mark.django_db
def test_create_cluster():
    # Create a new cluster
    cluster = Cluster.objects.create(name="Test Cluster", ram=32, cpu=8, gpu=2)

    # Assert the cluster was created successfully
    assert Cluster.objects.count() == 1
    assert cluster.name == "Test Cluster"
    assert cluster.ram == 32
    assert cluster.cpu == 8
    assert cluster.gpu == 2

@pytest.mark.django_db
def test_create_deployment():
    # Create a cluster
    cluster = Cluster.objects.create(name="Test Cluster", ram=32, cpu=8, gpu=2)

    # Create a deployment
    deployment = Deployment.objects.create(
        cluster=cluster,
        docker_image="nginx:latest",
        ram_required=16,
        cpu_required=1,
        gpu_required=0,
        priority=3,
        status="queued",
        created_at=now()
    )

    # Assert the deployment was created successfully
    assert Deployment.objects.count() == 1
    assert deployment.docker_image == "nginx:latest"
    assert deployment.status == "queued"
    assert deployment.priority == 3

@pytest.mark.django_db
def test_scheduler_updates_deployment_status():
    # Create a cluster
    cluster = Cluster.objects.create(name="Test Cluster", ram=32, cpu=8, gpu=2)

    # Create multiple deployments
    Deployment.objects.create(
        cluster=cluster,
        docker_image="nginx:latest",
        ram_required=16,
        cpu_required=1,
        gpu_required=0,
        priority=3,
        status="queued",
        created_at=now()
    )
    Deployment.objects.create(
        cluster=cluster,
        docker_image="redis:latest",
        ram_required=16,
        cpu_required=2,
        gpu_required=0,
        priority=2,
        status="queued",
        created_at=now()
    )

    # Run the scheduler
    deployment_scheduler()
    # Assert that deployments are updated to "completed"
    deployments = Deployment.objects.all()
    for deployment in deployments:
        assert deployment.status == "completed"

    # Assert that cluster resources are restored after deployments
    cluster.refresh_from_db()
    assert cluster.ram == 0
    assert cluster.cpu == 5
    assert cluster.gpu == 2
    cleanup_completed_deployments()