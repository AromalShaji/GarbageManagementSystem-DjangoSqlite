from email.policy import default
from django.db import models
from Home.models import Customer,Company
# Create your models here.

class Driver_offer(models.Model):
    companyid= models.ForeignKey('Home.Company', on_delete=models.CASCADE, default=None)
    vacancy=models.IntegerField(default="1")
    salary=models.CharField(max_length=100, default='1000')
    description=models.CharField(max_length=100, default='')
    start_time=models.CharField(max_length=100, default='9:00')
    end_time=models.CharField(max_length=100, default='6:00')
    status=models.BooleanField(max_length=100, default='1')
    
    def __str__(self):
        return str(self.companyid)
    
class Employee_offer(models.Model):
    companyid= models.ForeignKey('Home.Company', on_delete=models.CASCADE, default=None)
    vacancy=models.IntegerField(default="1")
    salary=models.CharField(max_length=100, default='1000')
    start_time=models.CharField(max_length=100, default='9:00')
    end_time=models.CharField(max_length=100, default='6:00')
    description=models.CharField(max_length=100, default='')
    status=models.BooleanField(max_length=100, default='1')
    
    def __str__(self):
        return str(self.companyid)
    
class vehicle(models.Model):
    companyid= models.ForeignKey('Home.Company', on_delete=models.CASCADE, default=None)
    vehicle_number=models.CharField(max_length=100, default='')
    status=models.BooleanField(max_length=100, default='1')
    
    def __str__(self):
        return str(self.vehicle_number)
    
class Dumbster(models.Model):
    companyid= models.ForeignKey('Home.Company', on_delete=models.CASCADE, default=None)
    number=models.CharField(max_length=100, default='')
    size=models.CharField(max_length=100, default='')
    dimension=models.CharField(max_length=100, default='')
    rate=models.CharField(max_length=100, default='')
    status=models.BooleanField(max_length=100, default='1')
    
    def __str__(self):
        return str(self.companyid)