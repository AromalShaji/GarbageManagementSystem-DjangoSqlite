from email.policy import default
from django.db import models

# Create your models here.


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50, default='')
    password = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=40, default='')
    location = models.CharField(max_length=20, default='')
    pincode = models.CharField(max_length=20, default='')
    status = models.BooleanField(default='1')
    role = models.CharField(max_length=100, default='customer')

    def __str__(self):
        return self.name


class Company(models.Model):
    cname = models.CharField(max_length=100)
    cemail = models.CharField(max_length=50, default='')
    cpassword = models.CharField(max_length=50, default='123')
    cphone = models.CharField(max_length=12)
    caddress = models.CharField(max_length=140, default='')
    clocation = models.CharField(max_length=20, default='')
    cpincode = models.CharField(max_length=20, default='')
    cfeatures = models.CharField(max_length=100, default='')
    carea = models.CharField(max_length=100,  default='')
    crate = models.CharField(max_length=100,  default='')
    cimg = models.ImageField(upload_to='images',  default='')
    status = models.BooleanField(default='1')
    role = models.CharField(max_length=100, default='company')

    def __str__(self):
        return self.cname


class Rate(models.Model):
    userid = models.ForeignKey(
        'Customer', on_delete=models.DO_NOTHING, default=None)
    companyid = models.ForeignKey(
        'Company', on_delete=models.DO_NOTHING, default=None)
    rate = models.CharField(max_length=100, default='1', null=True)
    cmt = models.CharField(max_length=250, null=True)

    def __str__(self):
        return str(self.userid) + " : " + str(self.companyid)


class driver_job_application(models.Model):
    userid = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, default=None)
    companyid = models.ForeignKey(
        'Company', on_delete=models.CASCADE, default=None)
    jobid = models.ForeignKey('Company.Driver_offer',
                              on_delete=models.CASCADE, default=None)
    phone = models.CharField(max_length=100, default='1')
    exp = models.CharField(max_length=100, default='1')
    limg = models.ImageField(upload_to='images',  default='')
    review = models.BooleanField(default='0')
    status = models.BooleanField(default='1')

    def __str__(self):
        return str(self.userid) + " : " + str(self.companyid)


class employee_job_application(models.Model):
    userid = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, default=None)
    companyid = models.ForeignKey(
        'Company', on_delete=models.CASCADE, default=None)
    jobid = models.ForeignKey('Company.Driver_offer',
                              on_delete=models.CASCADE, default=None)
    phone = models.CharField(max_length=100, default='1')
    review = models.BooleanField(default='0')
    status = models.BooleanField(default='1')

    def __str__(self):
        return str(self.userid) + " : " + str(self.companyid)


class service_booking(models.Model):
    userid = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, default=None)
    companyid = models.ForeignKey(
        'Company', on_delete=models.CASCADE, default=None)
    address = models.CharField(max_length=150, default="")
    location = models.CharField(max_length=20, default='')
    phone = models.CharField(max_length=20, default='')
    rate = models.CharField(max_length=20, default='')
    pincode = models.CharField(max_length=20, default='')
    time = models.CharField(max_length=30, default="4:00pm")
    date = models.DateField(null=True)
    feedback = models.CharField(max_length=220, default='', null=True)
    out_for_service = models.BooleanField(default='0')
    arrived_near = models.BooleanField(default='0')
    completed = models.BooleanField(default='0')
    latitude = models.CharField(max_length=230, default="", null=True)
    longitude = models.CharField(max_length=230, default="", null=True)
    status = models.BooleanField(default='1')

    def __str__(self):
        return str(self.userid) + " : " + str(self.companyid)


class dumbster_booking(models.Model):
    userid = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, default=None)
    companyid = models.ForeignKey(
        'Company', on_delete=models.CASCADE, default=None)
    dumbsterid = models.ForeignKey(
        'Company.Dumbster', on_delete=models.CASCADE, default=None)
    address = models.CharField(max_length=150, default="")
    location = models.CharField(max_length=20, default='')
    phone = models.CharField(max_length=20, default='')
    pincode = models.CharField(max_length=20, default='')
    numberofdumbster = models.IntegerField(default='1')
    date = models.DateField(null=True)
    numberofday = models.CharField(max_length=20, default='')
    rate = models.CharField(max_length=20, default='')
    size = models.CharField(max_length=20, default='')
    expire_date = models.CharField(max_length=20, default='')
    feedback = models.CharField(max_length=220, default='', null=True)
    out_for_service = models.BooleanField(default='0')
    arrived_near = models.BooleanField(default='0')
    completed = models.BooleanField(default='0')
    latitude = models.CharField(max_length=230, default="", null=True)
    longitude = models.CharField(max_length=230, default="", null=True)
    status = models.BooleanField(default='0')

    def __str__(self):
        return str(self.userid) + " : " + str(self.companyid)+" : " + str(self.date)


class payment(models.Model):
    userid = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, default=None)
    companyid = models.ForeignKey(
        'Company', on_delete=models.CASCADE, default=None)
    is_for = models.CharField(max_length=20, default='')
    date = models.CharField(max_length=20, default='')
    rate = models.CharField(max_length=20, default='')
    status = models.BooleanField(default='1')

    def __str__(self):
        return str(self.userid) + " : " + str(self.companyid)+" : " + str(self.is_for)
