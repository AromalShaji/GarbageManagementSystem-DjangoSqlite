from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.cache import cache_control
from Home.models import Customer, Company, Rate, driver_job_application, employee_job_application, dumbster_booking, service_booking
from .models import Driver_offer, Employee_offer, vehicle, Dumbster
from Employee.models import Employee, job_assigned, leave
from django.contrib import messages
from django.http import JsonResponse
from dateutil.rrule import rrule, DAILY
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from twilio.rest import Client
import os
# company reg page


def addcompanypage(request):
    return render(request, 'reg_company.html')

# driver reg page


def regjobdriverpage(request):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    vehicle_details = vehicle.objects.filter(
        status=1, companyid=companydetails)
    return render(request, 'reg_job_driver.html', {'vehicle_details': vehicle_details})

# employee reg page


def regjobemployeepage(request):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    vehicle_details = Driver_offer.objects.filter(companyid=companydetails)
    return render(request, 'reg_job_employee.html', {'vehicle_details': vehicle_details})

# driver job registration


def regjob_driver(request):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    if request.method == 'POST':
        salary = request.POST.get('salary')
        vacancy = request.POST.get('vacancy')
        desc = request.POST.get('desc')
        st_time = request.POST.get('start_time')
        ed_time = request.POST.get('end_time')
        ob = Driver_offer()
        ob.companyid = companydetails
        ob.vacancy = vacancy
        ob.salary = salary
        ob.description = desc
        ob.start_time = st_time
        ob.end_time = ed_time
        ob.status = '1'
        if (Driver_offer.objects.filter(companyid=companydetails, status=1)).exists():
            msg = "Already Provided a job offer for Drivers"
            return render(request, 'error.html', {'msg': msg})
        ob.save()
        messages.success(request, 'New Job Added')
        return redirect('profile_jobdetails')
    else:
        msg = "ERROR"
        return render(request, 'error.html', {'msg': msg})

# employee job registration


def regjob_employee(request):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    if request.method == 'POST':
        vacancy = request.POST.get('vacancy')
        st_time = request.POST.get('start_time')
        ed_time = request.POST.get('end_time')
        salary = request.POST.get('salary')
        desc = request.POST.get('desc')
        ob = Employee_offer()
        ob.companyid = companydetails
        ob.vacancy = vacancy
        ob.salary = salary
        ob.start_time = st_time
        ob.end_time = ed_time
        ob.description = desc
        ob.status = '1'
        if (Employee_offer.objects.filter(companyid=companydetails, status=1)).exists():
            msg = "Already Provided job offer for Driver!"
            return render(request, 'error.html', {'msg': msg})
        ob.save()
        messages.success(request, 'New Job Added')
        return redirect('profile_jobdetails')
    else:
        msg = "ERROR"
        return render(request, 'error.html', {'msg': msg})

# vehicle registration


def reg_vehicle(request):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    if request.method == 'POST':
        vnumber = request.POST.get('vehicle_number')
        ob = vehicle()
        ob.companyid = companydetails
        ob.vehicle_number = vnumber
        ob.status = 1
        if (vehicle.objects.filter(vehicle_number=vnumber, status=1)).exists():
            msg = "Vehicle name already exist!"
            return render(request, 'error.html', {'msg': msg})
        ob.save()
        messages.success(request, 'Vehicle Added')
        return redirect('profile_addvehicle')
    else:
        msg = "ERROR"
        return render(request, 'error.html', {'msg': msg})

# accept job driver offer from company


def driver_job_accept(request, vid, uname):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    dis = Customer.objects.get(name=uname)
    jid = Driver_offer.objects.get(companyid=companydetails)
    details = driver_job_application.objects.get(userid=dis, jobid=jid)
    name = details.userid
    ob = Employee()
    ob.userid = name
    ob.companyid = companydetails
    ob.eemail = dis.email
    ob.epassword = dis.password
    ob.ephone = dis.phone
    ob.status = 0
    ob.on_leave = 0
    ob.role = "driver"
    if (Employee.objects.filter(userid=dis)).exists():
        msg = "This User Already have a Job"
        return render(request, 'error.html', {'msg': msg})
    ob.save()
    driver_job_application.objects.filter(
        userid=dis, jobid=jid).update(review=1)
    empdetails = employee_job_application.objects.filter(userid=dis)
    for i in empdetails:
        cid = i.companyid
        x = Employee_offer.objects.get(companyid=cid)
        y = x.vacancy
        z = y+1
        Employee_offer.objects.filter(companyid=i.companyid).update(vacancy=z)
    drdetails = driver_job_application.objects.filter(
        userid=dis).exclude(companyid=companydetails)
    for i in drdetails:
        cid = i.companyid
        a = Driver_offer.objects.get(companyid=cid)
        b = a.vacancy
        c = b+1
        Driver_offer.objects.filter(companyid=i.companyid).update(vacancy=c)
    driver_job_application.objects.filter(
        userid=dis).exclude(companyid=companydetails).delete()
    employee_job_application.objects.filter(userid=dis).delete()
    html_template = 'email.html'
    email_msg = "🎊 Job Application Accepted 🎉"
    html_message = render_to_string(
        html_template, {'uname': name, 'email_msg': email_msg})
    subject = '🎉 Welcome to Eco-Cycle🔖 🌟'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [dis.email]
    message = EmailMessage(subject, html_message,
                           email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()
    messages.success(request, 'Accepted')
    return redirect('profile_jobapplications')

# accept job employee offer from company


def employee_job_accept(request, vid, uname):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    dis = Customer.objects.get(name=uname)
    jid = Driver_offer.objects.get(companyid=companydetails)
    details = employee_job_application.objects.get(userid=dis, jobid=jid)
    name = details.userid
    ob = Employee()
    ob.userid = name
    ob.eemail = dis.email
    ob.epassword = dis.password
    ob.ephone = dis.phone
    ob.companyid = companydetails
    ob.status = 0
    ob.on_leave = 0
    ob.role = "worker"
    if (Employee.objects.filter(userid=dis)).exists():
        msg = "This User Already have a Job"
        return render(request, 'error.html', {'msg': msg})
    ob.save()
    employee_job_application.objects.filter(
        userid=dis, jobid=jid).update(review=1)
    empdetails = employee_job_application.objects.filter(
        userid=dis).exclude(companyid=companydetails)
    for i in empdetails:
        cid = i.companyid
        x = Employee_offer.objects.get(companyid=cid)
        y = x.vacancy
        z = y+1
        Employee_offer.objects.filter(companyid=i.companyid).update(vacancy=z)
    drdetails = driver_job_application.objects.filter(userid=dis)
    for i in drdetails:
        cid = i.companyid
        a = Driver_offer.objects.get(companyid=cid)
        b = a.vacancy
        c = b+1
        Driver_offer.objects.filter(companyid=i.companyid).update(vacancy=c)
    employee_job_application.objects.filter(
        userid=dis).exclude(companyid=companydetails).delete()
    driver_job_application.objects.filter(userid=dis).delete()
    html_template = 'email.html'
    email_msg = "Job Application Accepted ⭐"
    html_message = render_to_string(
        html_template, {'uname': name, 'email_msg': email_msg})
    subject = '🌟 Welcome to Eco-Cycle 🌟'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [dis.email]
    message = EmailMessage(subject, html_message,
                           email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()
    messages.success(request, 'Accepted')
    return redirect('profile_jobapplications')

# provide dumbster page


def adddumbsterpage(request):
    return render(request, 'reg_dumbster.html')

# add dumbster


def adddumbster(request):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    if request.method == 'POST':
        number = request.POST.get('number')
        dimension = request.POST.get('dimension')
        rate = request.POST.get('rate')
        size = request.POST.get('size')
        ob = Dumbster()
        ob.companyid = companydetails
        ob.number = number
        ob.size = size
        ob.rate = rate
        ob.dimension = dimension
        ob.status = 1
        if (Dumbster.objects.filter(companyid=companydetails, status=1)).exists():
            msg = "Company already Added Dumbster"
            return render(request, 'error.html', {'msg': msg})
        ob.save()
        messages.success(request, 'Dumbster Added')
        return redirect('profile_dumbstermanager')
    else:
        msg = "ERROR"
        return render(request, 'error.html', {'msg': msg})

# driver job application reject in comapny profile


def driverjob_application_reject(request, uname):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    userdetails = Customer.objects.get(name=uname)
    driver_job_application.objects.filter(
        userid=userdetails, companyid=companydetails).delete()
    messages.success(request, 'Rejected')
    return redirect('profile_jobapplications')

# employee job application reject in comapny profile


def employeejob_application_reject(request, uname):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    userdetails = Customer.objects.get(name=uname)
    employee_job_application.objects.filter(
        userid=userdetails, companyid=companydetails).delete()
    messages.success(request, 'Rejected')
    return redirect('profile_jobapplications')

# make dumbster unavailable in companys profile


def dumbster_availablity(request):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    dumbsterdetails = Dumbster.objects.filter(companyid=dis)
    if (Dumbster.objects.filter(companyid=dis, status=1)):
        Dumbster.objects.filter(companyid=dis, status=1).update(status=0)
        messages.success(request, 'Updated')
        return redirect('profile_dumbstermanager')
    elif (Dumbster.objects.filter(companyid=dis, status=0)):
        Dumbster.objects.filter(companyid=dis, status=0).update(status=1)
        messages.success(request, 'Updated')
        return redirect('profile_dumbstermanager')
    else:
        msg = "ERROR"
        return render(request, 'error.html', {'msg': msg})

# dumbster details update


def dumbster_update(request):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    dumbsterdetails = Dumbster.objects.filter(companyid=dis)
    if request.method == "POST":
        numberofdumbster = request.POST.get('dumbster_number')
        dimension = request.POST.get('dumbster_dimension')
        rate = request.POST.get('dumbster_rate')
        size = request.POST.get('dumbster_size')
        Dumbster.objects.filter(companyid=dis).update(
            number=numberofdumbster, size=size, dimension=dimension, rate=rate)
        messages.success(request, 'Updated')
        return redirect('profile_dumbstermanager')
    else:
        msg = "ERROR"
        return render(request, 'error.html', {'msg': msg})

# job driver details update in companys profile


def jobdriverdetails_update(request):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    jobdriver_details = Driver_offer.objects.get(companyid=dis)
    if request.method == "POST":
        salary = request.POST.get('salary')
        vacancy = request.POST.get('vacancy')
        description = request.POST.get('description')
        start_times = request.POST.get('start_times')
        end_times = request.POST.get('end_times')
        Driver_offer.objects.filter(companyid=dis).update(
            salary=salary, vacancy=vacancy, description=description, start_time=start_times, end_time=end_times)
        messages.success(request, 'Updated')
        return redirect('profile_jobdetails')
    else:
        msg = "ERROR"
        return render(request, 'error.html', {'msg': msg})


# job employee details update in companys profile
def jobemployeedetails_update(request):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    jobdriver_details = Employee_offer.objects.get(companyid=dis)
    if request.method == "POST":
        salary = request.POST.get('salary')
        vacancy = request.POST.get('vacancy')
        description = request.POST.get('description')
        empstart_times = request.POST.get('start_times')
        empend_times = request.POST.get('end_times')
        Employee_offer.objects.filter(companyid=dis).update(
            salary=salary, vacancy=vacancy, description=description, start_time=empstart_times, end_time=empend_times)
        messages.success(request, 'Updated')
        return redirect('profile_jobdetails')
    msg = "ERROR!"
    return render(request, 'error.html', {'msg': msg})

# remove employee from the company using company profile


def remove_employee(request, ename, eemail):
    msg = ""
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    userdetails = Customer.objects.get(name=ename, email=eemail)
    employee_details = Employee.objects.get(
        userid=userdetails, eemail=eemail, companyid=dis)
    employee_role = employee_details.role
    if (employee_role == "driver"):
        msg = "Driver is removed from the Company"
        Customer.objects.filter(name=ename, email=eemail).update(status=1)
        driver_job_application.objects.filter(
            userid=userdetails, companyid=dis, review=1).delete()
        Employee.objects.filter(
            userid=userdetails, eemail=eemail, companyid=dis).delete()
        return redirect('employee_manager')
    elif (employee_role == "worker"):
        msg = "Worker is remover from the Company"
        Customer.objects.filter(name=ename, email=eemail).update(status=1)
        employee_job_application.objects.filter(
            userid=userdetails, companyid=dis, review=1).delete()
        Employee.objects.filter(
            userid=userdetails, eemail=eemail, companyid=dis).delete()
        messages.success(request, 'Removed Successfully')
        return redirect('employee_manager')
    else:
        msg = "ERROR!"
        return render(request, 'error.html', {'msg': msg})

# add employee page in companys profile


def add_employeepage(request):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    return render(request, 'addemployee_customer.html', {'dis': dis})

# add customer to the system using company


def addemployee_details(request):
    msg = ""
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        location = request.POST.get('location')
        pincode = request.POST.get('pincode')
        role = request.POST.get('role')
        ob = Customer()
        ob.name = name
        ob.email = email
        ob.password = password
        ob.phone = phone
        ob.address = address
        ob.location = location
        ob.pincode = pincode
        ob.status = 0
        ob.role = "customer"
        if (Customer.objects.filter(name=name, email=email)).exists():
            msg = "Username or Email Alredy exist"
            return render(request, 'error.html', {'msg': msg})
        email_msg = "Registration Successfull ✅"
        html_template = 'email.html'
        html_message = render_to_string(
            html_template, {'uname': name, 'email_msg': email_msg})
        subject = '🌟 Welcome to Eco-Cycle 🌟'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        message = EmailMessage(subject, html_message,
                               email_from, recipient_list)
        message.content_subtype = 'html'
        message.send()
        ob.save()
        return render(request, 'addemployee_to_company.html', {'name': name, 'email': email, 'password': password, 'phone': phone, 'address': address, 'location': location, 'pincode': pincode, 'role': role})
    else:
        msg = "ERROR"
        return render(request, 'error.html', {'msg': msg})

# add employee to the company


def addemployee(request):
    msg = ""
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        role = request.POST.get('role')
        ac = Employee()
        customerdetails = Customer.objects.get(name=name, email=email)
        ac.userid = customerdetails
        ac.eemail = email
        ac.epassword = password
        ac.ephone = phone
        ac.companyid = dis
        ac.status = 1
        ac.on_leave = 0
        ac.role = role
        if (Employee.objects.filter(userid=customerdetails, eemail=email)).exists():
            msg = "Username or Email Alredy exist"
            return render(request, 'error.html', {'msg': msg})
        if (job_assigned.objects.filter(employeeid=name, companyid=dis)).exists():
            msg = "Username or Email Alredy exist"
            return render(request, 'error.html', {'msg': msg})
        if (job_assigned.objects.filter(companyid=dis, employeeid="")).exists():
            job = job_assigned.objects.filter(companyid=dis, employeeid="")
            for i in job:
                job_assigned.objects.filter(
                    companyid=dis, employeeid="", id=i.id).update(employeeid=name)
        html_template = 'email.html'
        email_msg = "Job Application Accepted ⭐"
        html_message = render_to_string(
            html_template, {'uname': name, 'email_msg': email_msg})
        subject = '🌟 Welcome to Eco-Cycle 🌟'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        message = EmailMessage(subject, html_message,
                               email_from, recipient_list)
        message.content_subtype = 'html'
        message.send()
        ac.save()
        messages.success(request, 'Added Successfully')
        return redirect('employee_manager')
    else:
        msg = "ERROR"
        return render(request, 'error.html', {'msg': msg})

# removing added employee


def remove_addemployee(request, name, email, password):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    Customer.objects.filter(name=name, email=email, password=password).delete()
    job_assigned.objects.filter(companyid=dis, employeeid=name).delete()
    messages.success(request, 'Removed Successfully')
    return redirect('add_employeepage')

# make employee unavailable in companies profile


def make_employee_unavailable(request, name, email, role):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    userdetails = Customer.objects.get(name=name, email=email)
    employeedetails = Employee.objects.get(
        userid=userdetails, eemail=email, role=role, companyid=dis)
    if (employeedetails.status == 1):
        Employee.objects.filter(
            userid=userdetails, eemail=email, role=role).update(status=0)
    elif (employeedetails.status == 0):
        Employee.objects.filter(
            userid=userdetails, eemail=email, role=role).update(status=1)
    else:
        msg = "ERROR!"
        return render(request, 'error.html', {'msg': msg})
    messages.success(request, 'Updated')
    return redirect('employee_manager')

# assign job for employee


def assign_job(request):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    vehicle_details = " "
    worker = " "
    driver = " "
    dumbster = " "
    service = " "
    if request.method == "POST":
        vehicle_details = request.POST.get('vehicle')
        worker = request.POST.get('worker')
        driver = request.POST.get('driver')
        dumbster = request.POST.get('dumbster')
        service = request.POST.get('service')
        ob = job_assigned()
        ob.companyid = dis
        ob.employeeid = driver
        ob.assistant = worker
        ob.dumbster_scheduled = dumbster
        ob.service_scheduled = service
        if (service == ""):
            ob.time = ""
        else:
            customer = Customer.objects.get(name=service)
            if (service_booking.objects.filter(userid=customer, status=1)).exists():
                stime = service_booking.objects.get(userid=customer, status=1)
                # date driver
                if (Customer.objects.filter(name=driver)).exists():
                    dname = Customer.objects.get(name=driver)
                    if (Employee.objects.filter(userid=dname, companyid=dis)).exists():
                        emp = Employee.objects.get(userid=dname, companyid=dis)
                        ls = leave.objects.filter(
                            userid=emp, companyid=dis, approved=1, status=1)
                        for i in ls:
                            start = i.start_date
                            end = i.end_date
                            date_list = [dt.date() for dt in rrule(
                                DAILY, dtstart=start, until=end)]
                            for j in date_list:
                                if j == stime.date:
                                    msg = "Cannot assign job for driver on this date"
                                    return render(request, 'error.html', {'msg': msg})
                # date worker
                if (Customer.objects.filter(name=worker)).exists():
                    dname = Customer.objects.get(name=worker)
                    if (Employee.objects.filter(userid=dname, companyid=dis)).exists():
                        emp = Employee.objects.get(userid=dname, companyid=dis)
                        ls = leave.objects.filter(
                            userid=emp, companyid=dis, approved=1, status=1)
                        for i in ls:
                            start = i.start_date
                            end = i.end_date
                            date_list = [dt.date() for dt in rrule(
                                DAILY, dtstart=start, until=end)]
                            for j in date_list:
                                if j == stime.date:
                                    msg = "Cannot assign job for Assistant on this date"
                                    return render(request, 'error.html', {'msg': msg})
                if (job_assigned.objects.filter(companyid=dis, service_scheduled=service, date=stime.date, time=stime.time, status=1)).exists():
                    msg = "This service is already assigned for an employee. Try to update the data in update section..."
                    return render(request, 'error.html', {'msg': msg})
                ob.time = stime.time
                st = stime.time
                ob.date = stime.date
                sd = stime.date
                ob.latitude=stime.latitude
                ob.longitude=stime.longitude
        if (dumbster == ""):
            dd = ""
        else:
            customer = Customer.objects.get(name=dumbster)
            if (dumbster_booking.objects.filter(userid=customer, companyid=dis)).exclude(status="completed").exists():
                dtime = dumbster_booking.objects.get(
                    userid=customer, companyid=dis)
                # date driver
                if (Customer.objects.filter(name=driver)).exists():
                    dname = Customer.objects.get(name=driver)
                    if (Employee.objects.filter(userid=dname, companyid=dis)).exists():
                        emp = Employee.objects.get(userid=dname, companyid=dis)
                        ls = leave.objects.filter(
                            userid=emp, companyid=dis, approved=1, status=1)
                        for i in ls:
                            start = i.start_date
                            end = i.end_date
                            date_list = [dt.date() for dt in rrule(
                                DAILY, dtstart=start, until=end)]
                            for j in date_list:
                                if j == stime.date:
                                    msg = "Cannot assign job for driver on this date"
                                    return render(request, 'error.html', {'msg': msg})
                # date worker
                if (Customer.objects.filter(name=worker)).exists():
                    dname = Customer.objects.get(name=worker)
                    if (Employee.objects.filter(userid=dname, companyid=dis)).exists():
                        emp = Employee.objects.get(userid=dname, companyid=dis)
                        ls = leave.objects.filter(
                            userid=emp, companyid=dis, approved=1, status=1)
                        for i in ls:
                            start = i.start_date
                            end = i.end_date
                            date_list = [dt.date() for dt in rrule(
                                DAILY, dtstart=start, until=end)]
                            for j in date_list:
                                if j == stime.date:
                                    msg = "Cannot assign job for Assistant on this date"
                                    return render(request, 'error.html', {'msg': msg})
                if (job_assigned.objects.filter(companyid=dis, dumbster_scheduled=dumbster, date=dtime.date, status=1)).exists():
                    msg = "This service is already assigned for an employee. Try to update the data in update section..."
                    return render(request, 'error.html', {'msg': msg})
                ob.time = ""
                dt = ""
                ob.date = dtime.date
                dd = dtime.date
                ob.latitude=dtime.latitude
                ob.longitude=dtime.longitude
        if (job_assigned.objects.filter(companyid=dis, vehicle_detail=vehicle_details)).exclude(employeeid=driver).exists():
            msg = "Vechicle is not available"
            return render(request, 'error.html', {'msg': msg})
        else:
            ob.vehicle_detail = vehicle_details
        # check employee is available at this date
        if (service == ""):
            service = ""
        elif (job_assigned.objects.filter(employeeid=driver, companyid=dis, date=sd, time=st)).exists():
            msg = "Employee is not available at this time at this day!"
            return render(request, 'error.html', {'msg': msg})
        ob.save()
        messages.success(request, 'Job Assigned Successfully.')
        return redirect('employee_manager')

# update assigned job for employee


def update_assign_job(request, id):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    vehicle_details = " "
    worker = " "
    driver = " "
    dumbster = " "
    service = " "
    if request.method == "POST":
        vehicle_details = request.POST.get('vehicle')
        worker = request.POST.get('worker')
        driver = request.POST.get('driver')
        dumbster = request.POST.get('dumbster')
        service = request.POST.get('service')
        if dumbster and service:
            msg = "Can Only assign either dumbster service or waste collecting service !"
            return render(request, 'error.html', {'msg': msg})
        if (vehicle_details == ""):
            vehicle_details = "NILL"
        if (worker == ""):
            worker = "NILL"
        if (driver == ""):
            driver = "NILL"
        if (dumbster == ""):
            dumbster = "NILL"
        if (service == ""):
            service = "NILL"
        if (job_assigned.objects.filter(companyid=dis, vehicle_detail=vehicle_details)).exclude(employeeid=driver).exists():
            msg = "Vechicle is not available"
            return render(request, 'error.html', {'msg': msg})
        # update
        if (service == "NILL"):
            dumbsteruser = Customer.objects.get(name=dumbster)
            dumbster_time = dumbster_booking.objects.get(
                userid=dumbsteruser, companyid=dis)
            if (job_assigned.objects.filter(companyid=dis, assistant=worker, date=dumbster_time.date)).exclude(employeeid=driver).exclude(assistant="NILL").exists():
                msg = "Assistant is Not available at this date"
                return render(request, 'error.html', {'msg': msg})
            else:
                # date driver
                if (Customer.objects.filter(name=driver)).exists():
                    dname = Customer.objects.get(name=driver)
                    if (Employee.objects.filter(userid=dname, companyid=dis)).exists():
                        emp = Employee.objects.get(userid=dname, companyid=dis)
                        ls = leave.objects.filter(
                            userid=emp, companyid=dis, approved=1, status=1)
                        for i in ls:
                            start = i.start_date
                            end = i.end_date
                            date_list = [dt.date() for dt in rrule(
                                DAILY, dtstart=start, until=end)]
                            for j in date_list:
                                if j == dumbster_time.date:
                                    msg = "Cannot assign job for driver on this date"
                                    return render(request, 'error.html', {'msg': msg})
                # date worker
                if (Customer.objects.filter(name=worker)).exists():
                    dname = Customer.objects.get(name=worker)
                    if (Employee.objects.filter(userid=dname, companyid=dis)).exists():
                        emp = Employee.objects.get(userid=dname, companyid=dis)
                        ls = leave.objects.filter(
                            userid=emp, companyid=dis, approved=1, status=1)
                        for i in ls:
                            start = i.start_date
                            end = i.end_date
                            date_list = [dt.date() for dt in rrule(
                                DAILY, dtstart=start, until=end)]
                            for j in date_list:
                                if j == dumbster_time.date:
                                    msg = "Cannot assign job for Assistant on this date"
                                    return render(request, 'error.html', {'msg': msg})
                job_assigned.objects.filter(job_id=id).update(employeeid=driver, employeephone=dname.phone, vehicle_detail=vehicle_details,
                                                              assistant=worker, dumbster_scheduled=dumbster, service_scheduled=service, date=dumbster_time.date, time="", latitude=dumbster_time.latitude, longitude=dumbster_time.longitude)
        elif (dumbster == "NILL"):
            serviceuser = Customer.objects.get(name=service)
            service_time = service_booking.objects.get(
                userid=serviceuser, companyid=dis)
            if (job_assigned.objects.filter(companyid=dis, assistant=worker, date=service_time.date)).exclude(employeeid=driver).exclude(assistant="NILL").exists():
                msg = "Assistant is Not available at this date"
                return render(request, 'error.html', {'msg': msg})
            else:
                # date driver
                if (Customer.objects.filter(name=driver)).exists():
                    dname = Customer.objects.get(name=driver)
                    if (Employee.objects.filter(userid=dname, companyid=dis)).exists():
                        emp = Employee.objects.get(userid=dname, companyid=dis)
                        ls = leave.objects.filter(
                            userid=emp, companyid=dis, approved=1, status=1)
                        for i in ls:
                            start = i.start_date
                            end = i.end_date
                            date_list = [dt.date() for dt in rrule(
                                DAILY, dtstart=start, until=end)]
                            for j in date_list:
                                if j == service_time.date:
                                    msg = "Cannot assign job for driver on this date"
                                    return render(request, 'error.html', {'msg': msg})
                # date worker
                if (Customer.objects.filter(name=worker)).exists():
                    dname = Customer.objects.get(name=worker)
                    if (Employee.objects.filter(userid=dname, companyid=dis)).exists():
                        emp = Employee.objects.get(userid=dname, companyid=dis)
                        ls = leave.objects.filter(
                            userid=emp, companyid=dis, approved=1, status=1)
                        for i in ls:
                            start = i.start_date
                            end = i.end_date
                            date_list = [dt.date() for dt in rrule(
                                DAILY, dtstart=start, until=end)]
                            for j in date_list:
                                if j == service_time.date:
                                    msg = "Cannot assign job for Assistant on this date"
                                    return render(request, 'error.html', {'msg': msg})
                job_assigned.objects.filter(job_id=id).update(employeeid=driver, employeephone=dname.phone, vehicle_detail=vehicle_details,
                                                              assistant=worker, dumbster_scheduled=dumbster, service_scheduled=service, date=service_time.date, time=service_time.time,latitude=service_time.latitude, longitude=service_time.longitude)
        messages.success(request, 'Updated')
        return redirect('employee_manager')

# leave application approve


def leave_application_approve(request, id):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    leave.objects.filter(id=id).update(approved=1)
    messages.success(request, 'Leave approved')
    return redirect('employee_manager')

# leave application reject


def leave_application_reject(request, id):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    leave.objects.filter(id=id).update(rejected=1)
    messages.success(request, 'Leave application rejected')
    return redirect('employee_manager')
