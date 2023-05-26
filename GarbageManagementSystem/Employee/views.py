from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.cache import cache_control
from Home.models import Customer, Company, Rate, driver_job_application, employee_job_application, service_booking, dumbster_booking
from Home.models import payment
from Company.models import Driver_offer, Employee_offer, vehicle, Dumbster
from Employee.models import Employee, job_assigned, leave
from datetime import datetime, date, timedelta
import datetime
import random
from django.contrib import messages
from django.http import JsonResponse
from dateutil.rrule import rrule, DAILY
from datetime import datetime
from django.core.mail import send_mail
from ip2geotools.databases.noncommercial import DbIpCity
from ipware import get_client_ip
import json
import urllib

# updating out of service


def update_out_of_service(request, jid):
    if request.method == "POST":
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')
        id = request.session['id']
        email = request.session['email']
        dis = Employee.objects.get(id=id, eemail=email)
        employee = Customer.objects.get(name=dis.userid)
        companydetails = Company.objects.get(cname=dis.companyid)
        job = job_assigned.objects.get(job_id=jid)
        if (job.service_scheduled == "NILL" or job.service_scheduled == ""):
            customer = Customer.objects.get(name=job.dumbster_scheduled)
            if (job.recollect_dumbster == 1):
                dumbster = dumbster_booking.objects.get(
                    userid=customer, companyid=companydetails, address=job.address, location=job.location, phone=job.phone, pincode=job.pincode)
                if (job.out_for_service == 0):
                    job_assigned.objects.filter(job_id=jid).update(
                        out_for_service=1, status=0)
                elif (job.out_for_service == 1):
                    job_assigned.objects.filter(job_id=jid).update(
                        out_for_service=0, status=1)
            else:
                dumbster = dumbster_booking.objects.get(userid=customer, companyid=companydetails, address=job.address,
                                                        location=job.location, phone=job.phone, pincode=job.pincode, date=job.date)
                if (dumbster.out_for_service == 0):
                    dumbster_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address, location=job.location,
                                                    phone=job.phone, pincode=job.pincode, date=job.date).update(out_for_service=1, status=0, latitude=lat, longitude=lon)
                elif (dumbster.out_for_service == 1):
                    dumbster_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address, location=job.location,
                                                    phone=job.phone, pincode=job.pincode, date=job.date).update(out_for_service=0, status=1, latitude=lat, longitude=lon)
                if (job.out_for_service == 0):
                    job_assigned.objects.filter(job_id=jid).update(
                        out_for_service=1, status=0)
                elif (job.out_for_service == 1):
                    job_assigned.objects.filter(job_id=jid).update(
                        out_for_service=0, status=1)
            return redirect('employeehome')
        elif (job.dumbster_scheduled == "NILL" or job.dumbster_scheduled == ""):
            customer = Customer.objects.get(name=job.service_scheduled)
            service = service_booking.objects.get(userid=customer, companyid=companydetails, address=job.address,
                                                  location=job.location, phone=job.phone, pincode=job.pincode, date=job.date, time=job.time)
            if (service.out_for_service == 0):
                service_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address, location=job.location,
                                               phone=job.phone, pincode=job.pincode, date=job.date, time=job.time).update(out_for_service=1, latitude=lat, longitude=lon)
            elif (service.out_for_service == 1):
                service_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address, location=job.location,
                                               phone=job.phone, pincode=job.pincode, date=job.date, time=job.time).update(out_for_service=0, latitude=lat, longitude=lon)
            if (job.out_for_service == 0):
                job_assigned.objects.filter(
                    job_id=jid).update(out_for_service=1)
            elif (job.out_for_service == 1):
                job_assigned.objects.filter(
                    job_id=jid).update(out_for_service=0)
            return redirect('employeehome')
    else:
        msg = "ERROR"
        return render(request, 'error.html', {'msg': msg})

# updating arrive near


def update_arrived_near(request, jid):
    if request.method == "POST":
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')
        id = request.session['id']
        email = request.session['email']
        dis = Employee.objects.get(id=id, eemail=email)
        employee = Customer.objects.get(name=dis.userid)
        companydetails = Company.objects.get(cname=dis.companyid)
        job = job_assigned.objects.get(job_id=jid)
        if (job.service_scheduled == "NILL" or job.service_scheduled == ""):
            customer = Customer.objects.get(name=job.dumbster_scheduled)
            if (job.recollect_dumbster == 1):
                dumbster = dumbster_booking.objects.get(
                    userid=customer, companyid=companydetails, address=job.address, location=job.location, phone=job.phone, pincode=job.pincode)
                if (job.arrived_near == 0):
                    job_assigned.objects.filter(job_id=jid).update(
                        arrived_near=1, status=0)
                elif (job.arrived_near == 1):
                    job_assigned.objects.filter(job_id=jid).update(
                        arrived_near=0, status=1)
            else:
                dumbster = dumbster_booking.objects.get(userid=customer, companyid=companydetails, address=job.address,
                                                        location=job.location, phone=job.phone, pincode=job.pincode, date=job.date)
                if (dumbster.arrived_near == 0):
                    dumbster_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address, location=job.location,
                                                    phone=job.phone, pincode=job.pincode, date=job.date).update(arrived_near=1, status=0, latitude=lat, longitude=lon)
                elif (dumbster.arrived_near == 1):
                    dumbster_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address, location=job.location,
                                                    phone=job.phone, pincode=job.pincode, date=job.date).update(arrived_near=0, status=1, latitude=lat, longitude=lon)
                if (job.arrived_near == 0):
                    job_assigned.objects.filter(job_id=jid).update(
                        arrived_near=1, status=0)
                elif (job.arrived_near == 1):
                    job_assigned.objects.filter(job_id=jid).update(
                        arrived_near=0, status=1)
            return redirect('employeehome')
        elif (job.dumbster_scheduled == "NILL" or job.dumbster_scheduled == ""):
            customer = Customer.objects.get(name=job.service_scheduled)
            service = service_booking.objects.get(userid=customer, companyid=companydetails, address=job.address,
                                                location=job.location, phone=job.phone, pincode=job.pincode, date=job.date, time=job.time)
            if (service.arrived_near == 0):
                service_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address, location=job.location,
                                            phone=job.phone, pincode=job.pincode, date=job.date, time=job.time).update(arrived_near=1, latitude=lat, longitude=lon)
            elif (service.arrived_near == 1):
                service_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address, location=job.location,
                                            phone=job.phone, pincode=job.pincode, date=job.date, time=job.time).update(arrived_near=0, latitude=lat, longitude=lon)
            if (job.arrived_near == 0):
                job_assigned.objects.filter(job_id=jid).update(arrived_near=1)
            elif (job.arrived_near == 1):
                job_assigned.objects.filter(job_id=jid).update(arrived_near=0)
            return redirect('employeehome')

# updating complete


def update_completed(request, jid):
    if request.method == "POST":
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')
        id = request.session['id']
        email = request.session['email']
        dis = Employee.objects.get(id=id, eemail=email)
        employee = Customer.objects.get(name=dis.userid)
        companydetails = Company.objects.get(cname=dis.companyid)
        job = job_assigned.objects.get(job_id=jid)
        if (job.service_scheduled == "NILL" or job.service_scheduled == ""):
            customer = Customer.objects.get(name=job.dumbster_scheduled)
            if (job.recollect_dumbster == 1):
                dumbster = dumbster_booking.objects.get(
                    userid=customer, companyid=companydetails, address=job.address, location=job.location, phone=job.phone, pincode=job.pincode)
                if (job.completed == 0):
                    job_assigned.objects.filter(
                        job_id=jid).update(completed=1, status=0)
                elif (job.completed == 1):
                    job_assigned.objects.filter(
                        job_id=jid).update(completed=0, status=1)
            else:
                dumbster = dumbster_booking.objects.get(userid=customer, companyid=companydetails, address=job.address,
                                                        location=job.location, phone=job.phone, pincode=job.pincode, date=job.date)
                if (dumbster.completed == 0):
                    dumbster_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address,
                                                    location=job.location, phone=job.phone, pincode=job.pincode, date=job.date).update(completed=1, status=0, latitude=lat, longitude=lon)
                elif (dumbster.completed == 1):
                    dumbster_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address,
                                                    location=job.location, phone=job.phone, pincode=job.pincode, date=job.date).update(completed=0, status=1, latitude=lat, longitude=lon)
                if (job.completed == 0):
                    job_assigned.objects.filter(
                        job_id=jid).update(completed=1, status=0)
                elif (job.completed == 1):
                    job_assigned.objects.filter(
                        job_id=jid).update(completed=0, status=1)
            return redirect('employeehome')
        elif (job.dumbster_scheduled == "NILL" or job.dumbster_scheduled == ""):
            customer = Customer.objects.get(name=job.service_scheduled)
            service = service_booking.objects.get(userid=customer, companyid=companydetails, address=job.address,
                                                location=job.location, phone=job.phone, pincode=job.pincode, date=job.date, time=job.time)
            if (service.completed == 0):
                service_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address, location=job.location,
                                            phone=job.phone, pincode=job.pincode, date=job.date, time=job.time).update(completed=1, status=0, latitude=lat, longitude=lon)
            elif (service.completed == 1):
                service_booking.objects.filter(userid=customer, companyid=companydetails, address=job.address, location=job.location,
                                            phone=job.phone, pincode=job.pincode, date=job.date, time=job.time).update(completed=0, status=1, latitude=lat, longitude=lon)
            if (job.completed == 0):
                job_assigned.objects.filter(
                    job_id=jid).update(completed=1, status=0)
            elif (job.completed == 1):
                job_assigned.objects.filter(
                    job_id=jid).update(completed=0, status=1)
            return redirect('employeehome')

# apply for leaave


def employee_leave(request):
    today = datetime.now().strftime('%Y-%m-%d')
    id = request.session['id']
    email = request.session['email']
    dis = Employee.objects.get(id=id, eemail=email)
    employee = Customer.objects.get(name=dis.userid)
    companydetails = Company.objects.get(cname=dis.companyid)
    if request.method == 'POST':
        st_date = request.POST.get('start_date')
        ed_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        if (today > st_date):
            msg = "Check the date.!"
            return render(request, 'error.html', {'msg': msg})
        elif (today > ed_date):
            msg = "Check the date.!"
            return render(request, 'error.html', {'msg': msg})
        elif (ed_date < st_date):
            msg = "Check the date.!"
            return render(request, 'error.html', {'msg': msg})
        ob = leave()
        ob.userid = dis
        ob.companyid = companydetails
        ob.start_date = st_date
        ob.end_date = ed_date
        ob.reason = reason
        ob.approved = 0
        ob.rejected = 0
        ob.status = 1
        ob.role = dis.role
        start = datetime.strptime(st_date, '%Y-%m-%d').date()
        end = datetime.strptime(ed_date, '%Y-%m-%d').date()
        date_list = [dt.strftime("%Y-%m-%d")
                     for dt in rrule(DAILY, dtstart=start, until=end)]
        for i in date_list:
            if (job_assigned.objects.filter(employeeid=dis.userid, companyid=companydetails, date=i) | job_assigned.objects.filter(assistant=dis.userid, companyid=companydetails, date=i)).exists():
                msg = "Job is assigned at these date. Contact your company"
                return render(request, 'error.html', {'msg': msg})
            elif (leave.objects.filter(userid=dis, companyid=companydetails, status=1, start_date=i) | leave.objects.filter(userid=dis, companyid=companydetails, status=1, end_date=i)).exists():
                msg = "Already applied!..."
                return render(request, 'error.html', {'msg': msg})
        ob.save()
        messages.success(request, 'Leave application submitted')
        return redirect('employeehome')
