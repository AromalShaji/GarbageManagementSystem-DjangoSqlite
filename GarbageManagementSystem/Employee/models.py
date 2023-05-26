from django.db import models
from Home.models import Customer, Company
from Company.models import vehicle
# Create your models here.


class Employee(models.Model):
    userid = models.ForeignKey(
        'Home.Customer', on_delete=models.CASCADE, default=None)
    eemail = models.CharField(max_length=50, default="")
    epassword = models.CharField(max_length=50, default="")
    ephone = models.CharField(max_length=50, default="")
    companyid = models.ForeignKey(
        'Home.Company', on_delete=models.CASCADE, default=None)
    status = models.BooleanField(max_length=100, default='1')
    on_leave = models.BooleanField(default='0')
    role = models.CharField(max_length=50, default=" ")

    def __str__(self):
        return str(self.userid)+" : " + str(self.companyid)+" : " + str(self.role)


class job_assigned(models.Model):
    job_id = models.AutoField(primary_key=True)
    companyid = models.ForeignKey(
        'Home.Company', on_delete=models.CASCADE, default=None)
    employeeid = models.CharField(max_length=50, default="")
    employeephone = models.CharField(max_length=50, default="", null=True)
    assistant = models.CharField(max_length=50, default="", null=True)
    vehicle_detail = models.CharField(max_length=50, default="", null=True)
    dumbster_scheduled = models.CharField(max_length=50, default="", null=True)
    service_scheduled = models.CharField(max_length=50, default="", null=True)
    address = models.CharField(max_length=150, default="")
    location = models.CharField(max_length=20, default='')
    phone = models.CharField(max_length=20, default='')
    pincode = models.CharField(max_length=20, default='')
    date = models.DateField(null=True, blank=True)
    time = models.CharField(max_length=50, default="", null=True)
    latitude = models.CharField(max_length=230, default="", null=True)
    longitude = models.CharField(max_length=230, default="", null=True)
    recollect_dumbster = models.BooleanField(default='0')
    out_for_service = models.BooleanField(default='0')
    arrived_near = models.BooleanField(default='0')
    completed = models.BooleanField(default='0')
    status = models.BooleanField(default='0')

    def __str__(self):
        return str(self.job_id)+" : "+str(self.employeeid)+" : " + str(self.companyid)+" : " + str(self.vehicle_detail)+" : " + str(self.dumbster_scheduled)+" : " + str(self.service_scheduled)+" : " + str(self.date)


class leave(models.Model):
    userid = models.ForeignKey(
        'Employee', on_delete=models.CASCADE, default=None)
    companyid = models.ForeignKey(
        'Home.Company', on_delete=models.CASCADE, default=None)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    reason = models.CharField(max_length=50, default="", null=True)
    approved = models.BooleanField(max_length=100, default='0')
    rejected = models.BooleanField(max_length=100, default='0')
    status = models.BooleanField(max_length=100, default='0')
    role = models.CharField(max_length=50, default="", null=True)

    def __str__(self):
        return str(self.userid)+" : " + str(self.companyid)+" : " + str(self.approved)+" : " + str(self.start_date)+" : " + str(self.end_date)
