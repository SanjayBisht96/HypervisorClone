from django.contrib import admin
from .models import User, Organization, InviteCode
# Register your models here.
admin.site.register(User)
admin.site.register(Organization)
admin.site.register(InviteCode)