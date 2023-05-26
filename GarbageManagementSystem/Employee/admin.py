from django.contrib import admin
from .models import Employee,job_assigned,leave
# Register your models here.

admin.site.register(Employee)
admin.site.register(job_assigned)
admin.site.register(leave)