from django.contrib import admin
from .models import Customer,Company,Rate,driver_job_application,employee_job_application,service_booking,dumbster_booking
from .models import payment
# Register your models here.
admin.site.register(Customer)
admin.site.register(Company)
admin.site.register(Rate)
admin.site.register(driver_job_application)
admin.site.register(employee_job_application)
admin.site.register(service_booking)
admin.site.register(dumbster_booking)
admin.site.register(payment)