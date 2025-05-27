from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    organization = models.ForeignKey('Organization', on_delete=models.SET_NULL, null=True, blank=True)

class Organization(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class InviteCode(models.Model):
    code = models.CharField(max_length=10, unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
