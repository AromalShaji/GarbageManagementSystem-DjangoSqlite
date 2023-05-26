from django.shortcuts import render
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.cache import cache_control
from .models import Customer, Company, Rate, driver_job_application, employee_job_application, service_booking, dumbster_booking
from .models import payment
from Company.models import Driver_offer, Employee_offer, vehicle, Dumbster
from Employee.models import Employee, job_assigned, leave
from datetime import datetime, date, timedelta
import datetime
import random
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from dateutil.rrule import rrule, DAILY
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from twilio.rest import Client
import os
from io import BytesIO
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from reportlab.pdfgen import canvas
import json
from urllib.parse import urlencode
import zipfile
from twilio.base.exceptions import TwilioRestException
# home


def index(request):
    today = datetime.datetime.now().date()
    company_details = Company.objects.filter(status=1)
    job_driver = Driver_offer.objects.filter(vacancy__gt=0, status=1)
    job_employee = Employee_offer.objects.filter(vacancy__gt=0, status=1)
    dumbster_details = Dumbster.objects.filter(status=1)
    leave_status = leave.objects.filter(approved=1, status=1)
    for i in leave_status:
        if (i.start_date <= today) and (i.end_date >= today):
            emp = Customer.objects.get(name=i.userid.userid)
            Employee.objects.filter(userid=emp).update(on_leave=1)
        elif (i.end_date < today):
            emp = Customer.objects.get(name=i.userid.userid)
            Employee.objects.filter(userid=emp).update(on_leave=0)
            leave_emp = Employee.objects.get(userid=emp)
            leave.objects.filter(userid=leave_emp).update(status=0)
    if 'id' in request.session:
        leave_status = leave.objects.filter(approved=1, status=1)
        for i in leave_status:
            if (i.start_date <= today) and (i.end_date >= today):
                emp = Customer.objects.get(name=i.userid.userid)
                Employee.objects.filter(userid=emp).update(on_leave=1)
            elif (i.end_date < today):
                emp = Customer.objects.get(name=i.userid.userid)
                Employee.objects.filter(userid=emp).update(on_leave=0)
                leave_emp = Employee.objects.get(userid=emp)
                leave.objects.filter(userid=leave_emp).update(status=0)
        id = request.session['id']
        email = request.session['email']
        if (Customer.objects.filter(id=id, email=email)).exists():
            dis = Customer.objects.get(id=id)
            req_accepted = Employee.objects.filter(userid=dis)
            driver_job_applied = driver_job_application.objects.filter(
                userid=dis)
            employee_job_applied = employee_job_application.objects.filter(
                userid=dis)
            service_booked = service_booking.objects.filter(userid=dis)
            dumbster_booked = dumbster_booking.objects.filter(userid=dis)
            cnt = len(service_booked)+len(dumbster_booked)
            return render(request, 'index.html', {'id': id, 'dis': dis, 'company_details': company_details, 'job_driver': job_driver, 'job_employee': job_employee, 'driver_job_applied': driver_job_applied, 'employee_job_applied': employee_job_applied, 'req_accepted': req_accepted, 'service_booked': service_booked, 'dumbster_details': dumbster_details, 'dumbster_booked': dumbster_booked, 'cnt': cnt, 'today': today})
        elif (Company.objects.filter(id=id, cemail=email)).exists():
            dis = Company.objects.get(id=id)
            driver_job_applied = driver_job_application.objects.filter(
                companyid=dis, status=1)
            employee_job_applied = employee_job_application.objects.filter(
                companyid=dis, status=1)
            offer_accept = Employee.objects.filter(companyid=dis, status=1)
            service_booked = service_booking.objects.filter(companyid=dis)
            dumbster_booked = dumbster_booking.objects.filter(companyid=dis)
            leave_status = leave.objects.filter(companyid=dis, status=1)
            return render(request, 'index.html', {'id': id, 'dis': dis, 'company_details': company_details, 'job_driver': job_driver, 'job_employee': job_employee, 'driver_job_applied': driver_job_applied, 'employee_job_applied': employee_job_applied, 'offer_accept': offer_accept, 'dumbster_details': dumbster_details, 'dumbster_booked': dumbster_booked, 'service_booked': service_booked, 'leave_status': leave_status, 'today': today})
        elif (Employee.objects.filter(id=id, eemail=email)).exists():
            return redirect('employeehome')
        else:
            msg = "ERROR"
            return render(request, 'error.html', {'msg': msg})
    else:
        return render(request, 'index.html', {'company_details': company_details, 'job_driver': job_driver, 'job_employee': job_employee, 'dumbster_details': dumbster_details})

# employee home


def employeehome(request):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    id = request.session['id']
    email = request.session['email']
    dis = Employee.objects.get(id=id, eemail=email)
    customer = Customer.objects.get(name=dis.userid)
    companydetails = Company.objects.get(cname=dis.companyid)
    service_booked = service_booking.objects.filter(userid=customer, status=1)
    dumbster_booked = dumbster_booking.objects.filter(userid=customer)
    service = service_booking.objects.filter(companyid=companydetails)
    cnt = len(service_booked)+len(dumbster_booked)
    if (dis.role == "driver"):
        job = job_assigned.objects.filter(
            companyid=companydetails, employeeid=dis.userid, date=today)
        jobcnt = job_assigned.objects.filter(
            companyid=companydetails, employeeid=dis.userid)
        jobtoday = job_assigned.objects.filter(
            companyid=companydetails, employeeid=dis.userid, date__gt=today).order_by('date')
        totaljobcount = len(jobcnt)
        dum = job_assigned.objects.filter(employeeid=dis.userid, service_scheduled="NILL") | job_assigned.objects.filter(
            employeeid=dis.userid, service_scheduled="")
        dum_len = len(dum)
        ser = job_assigned.objects.filter(employeeid=dis.userid, dumbster_scheduled="NILL") | job_assigned.objects.filter(
            employeeid=dis.userid, dumbster_scheduled="")
        ser_len = len(ser)
        ttl_completed = job_assigned.objects.filter(
            employeeid=dis.userid, status=0)
        ttl_cmp_len = len(ttl_completed)
        leave_status = leave.objects.filter(
            userid=dis, companyid=companydetails, status=1, role='driver')
        ls = leave.objects.filter(
            userid=dis, companyid=companydetails, approved=1, role='driver')
        ls_cnt = 0
        for i in ls:
            start = i.start_date
            end = i.end_date
            date_list = [dt.strftime("%Y-%m-%d")
                         for dt in rrule(DAILY, dtstart=start, until=end)]
            for j in date_list:
                ls_cnt = ls_cnt+1
        return render(request, 'employee.html', {'dis': dis, 'companydetails': companydetails, 'service': service, 'service_booked': service_booked, 'dumbster_booked': dumbster_booked, 'cnt': cnt, 'job': job, 'totaljobcount': totaljobcount, 'dum_len': dum_len, 'ser_len': ser_len, 'ttl_cmp_len': ttl_cmp_len, 'today': today, 'jobtoday': jobtoday, 'leave_status': leave_status, 'ls_cnt': ls_cnt})
    elif (dis.role == "worker"):
        job = job_assigned.objects.filter(
            companyid=companydetails, assistant=dis.userid, date=today)
        jobcnt = job_assigned.objects.filter(
            companyid=companydetails, assistant=dis.userid)
        jobtoday = job_assigned.objects.filter(
            companyid=companydetails, assistant=dis.userid, date__gt=today).order_by('date')
        totaljobcount = len(jobcnt)
        dum = job_assigned.objects.filter(assistant=dis.userid, service_scheduled="NILL") | job_assigned.objects.filter(
            assistant=dis.userid, service_scheduled="")
        dum_len = len(dum)
        ser = job_assigned.objects.filter(assistant=dis.userid, dumbster_scheduled="NILL") | job_assigned.objects.filter(
            assistant=dis.userid, dumbster_scheduled="")
        ser_len = len(ser)
        ttl_completed = job_assigned.objects.filter(
            assistant=dis.userid, status=0)
        ttl_cmp_len = len(ttl_completed)
        leave_status = leave.objects.filter(
            userid=dis, companyid=companydetails, status=1, role='worker')
        ls = leave.objects.filter(
            userid=dis, companyid=companydetails, approved=1, role='worker')
        ls_cnt = 0
        for i in ls:
            start = i.start_date
            end = i.end_date
            date_list = [dt.strftime("%Y-%m-%d")
                         for dt in rrule(DAILY, dtstart=start, until=end)]
            for j in date_list:
                ls_cnt = ls_cnt+1
        return render(request, 'employee.html', {'dis': dis, 'companydetails': companydetails, 'service': service, 'service_booked': service_booked, 'dumbster_booked': dumbster_booked, 'cnt': cnt, 'job': job, 'totaljobcount': totaljobcount, 'dum_len': dum_len, 'ser_len': ser_len, 'ttl_cmp_len': ttl_cmp_len, 'today': today, 'jobtoday': jobtoday, 'leave_status': leave_status, 'ls_cnt': ls_cnt})
    msg = "ERROR"
    return render(request, 'error.html', {'msg': msg})

# login


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if request.method == 'POST':
        useremail = request.POST.get('useremail')
        password = request.POST.get('password')
        if (Customer.objects.filter(email=useremail, password=password, status=1)).exists():
            user_details = Customer.objects.get(
                email=useremail, password=password)
            user_id = user_details.id
            user_email = user_details.email
            request.session['id'] = user_id
            request.session['email'] = user_email
            return redirect('index')
        elif (Company.objects.filter(cemail=useremail, cpassword=password, status=1)).exists():
            company_details = Company.objects.get(
                cemail=useremail, cpassword=password)
            company_id = company_details.id
            company_email = company_details.cemail
            request.session['id'] = company_id
            request.session['email'] = company_email
            return redirect('index')
        elif (Employee.objects.filter(eemail=useremail, epassword=password, status=1)).exists():
            dis = Employee.objects.get(
                eemail=useremail, epassword=password, status=1)
            companydetails = Company.objects.get(cname=dis.companyid)
            request.session['id'] = dis.id
            request.session['email'] = dis.eemail
            return redirect('employeehome')
        else:
            msg = "wrong user name or password or account does not exist!!"
            return render(request, 'error.html', {'msg': msg})
    return render(request, 'login.html')

# logout


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def lgout(request):
    request.session.flush()
    return redirect('index')

# registration


def reg(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        mail = request.POST.get('email')
        pwd = request.POST.get('password')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        location = request.POST.get('location')
        pincode = request.POST.get('pincode')
        ob = Customer()
        ob.name = uname
        ob.email = mail
        ob.password = pwd
        ob.phone = phone
        ob.address = address
        ob.location = location
        ob.pincode = pincode
        ob.role = "customer"
        if (Customer.objects.filter(name=uname)).exists():
            msg = "User name already exist!!"
            return render(request, 'error.html', {'msg': msg})
        if (Customer.objects.filter(email=mail)).exists():
            msg = "Email already exist!!"
            return render(request, 'error.html', {'msg': msg})
        if (Company.objects.filter(cemail=mail)).exists():
            msg = "Email already exist!!"
            return render(request, 'error.html', {'msg': msg})
        ob.status = 1
        email_msg = "Registration Successfull ✅"
        html_template = 'email.html'
        html_message = render_to_string(
            html_template, {'uname': uname, 'email_msg': email_msg})
        subject = '🎉 Welcome to Eco-Cycle 🌟'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [mail]
        message = EmailMessage(subject, html_message,
                               email_from, recipient_list)
        message.content_subtype = 'html'
        message.send()
        account_sid = "your sid"
        auth_token = "token"
        client = Client(account_sid, auth_token)
        try:
            message = client.messages.create(
                body="ECO-CYCLE ♻ : Account created successfully ✅",
                from_="+16073054817",
                to=phone
            )
            print("Message sent successfully!")
        except TwilioRestException as e:
            print("Error sending message:", e)
        ob.save()
        messages.success(request, 'Registered Successfully')
        return redirect('login')
    else:
        messages.success(request, 'ERROR!')
        return render(request, 'signup.html')

# company registration


def companyreg(request):
    if request.method == 'POST':
        coname = request.POST.get('cname')
        cmail = request.POST.get('cmail')
        cpwd = request.POST.get('cpassword')
        cphone = request.POST.get('cphone')
        caddress = request.POST.get('caddress')
        clocation = request.POST.get('clocation')
        cpincode = request.POST.get('cpincode')
        cfeatures = request.POST.get('feat')
        carea = request.POST.get('carea')
        crate = request.POST.get('crate')
        cimg = request.FILES['image']
        role = 'company'
        ob = Company()
        ob.cname = coname
        ob.cemail = cmail
        ob.cpassword = cpwd
        ob.cphone = cphone
        ob.caddress = caddress
        ob.clocation = clocation
        ob.cpincode = cpincode
        ob.cfeatures = cfeatures
        ob.carea = carea
        ob.crate = crate
        ob.cimg = cimg
        ob.role = role
        if (Company.objects.filter(cname=coname, cemail=cmail)).exists():
            msg = "Company name already exist!!"
            return render(request, 'error.html', {'msg': msg})
        if (Company.objects.filter(cemail=cmail)).exists():
            msg = "Email already exist!!"
            return render(request, 'error.html', {'msg': msg})
        if (Customer.objects.filter(email=cmail)).exists():
            msg = "Email already exist!!"
            return render(request, 'error.html', {'msg': msg})
        ob.status = 1
        html_template = 'email.html'
        email_msg = "Registration Successful ✅"
        html_message = render_to_string(
            html_template, {'uname': coname, 'email_msg': email_msg})
        subject = '🎉 Welcome to Eco-Cycle 🌟'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [cmail]
        message = EmailMessage(subject, html_message,
                               email_from, recipient_list)
        message.content_subtype = 'html'
        message.send()
        # account_sid = "your sid"
        # auth_token = "token"
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body="ECO-CYCLE ♻ : Account created successfully ✅",
        #     from_="+16073054817",
        #     to=cphone
        # )
        ob.save()
        messages.success(request, 'Registered Successfully')
        return redirect('signin')
    else:
        messages.success(request, 'ERROR!')
        return render(request, 'reg_company.html')

# registration page


def signup(request):
    return render(request, 'signup.html')

# login page


def signin(request):
    return render(request, 'login.html')

# company details


def companydetails(request, id):
    companydetails = Company.objects.get(id=id)
    company_id = companydetails.id
    rating = Rate.objects.filter(companyid=companydetails)
    driver_details = Driver_offer.objects.filter(
        vacancy__gt=0, companyid=companydetails)
    employee_details = Employee_offer.objects.filter(
        vacancy__gt=0, companyid=companydetails)
    if (Dumbster.objects.filter(companyid=companydetails, status=1)).exists():
        dumbster_details = Dumbster.objects.get(
            companyid=companydetails, status=1)
    else:
        dumbster_details = ""
    if 'id' in request.session:
        reqid = request.session['id']
        email = request.session['email']
        if (Customer.objects.filter(id=reqid, email=email)).exists():
            dis = Customer.objects.get(id=reqid)
            return render(request, 'company_details.html', {'id': reqid, 'dis': dis, 'companydetails': companydetails, 'rating': rating, 'driver_details': driver_details, 'employee_details': employee_details, 'dumbster_details': dumbster_details})
        elif (Company.objects.filter(id=reqid, cemail=email)).exists():
            dis = Company.objects.get(id=reqid)
            return render(request, 'company_details.html', {'id': reqid, 'dis': dis, 'companydetails': companydetails, 'rating': rating, 'driver_details': driver_details, 'employee_details': employee_details, 'dumbster_details': dumbster_details})
        else:
            msg = "ERROR"
            return render(request, 'error.html', {'msg': msg})
    else:
        return render(request, 'company_details.html', {'companydetails': companydetails, 'companyid': company_id, 'rating': rating, 'driver_details': driver_details, 'employee_details': employee_details, 'dumbster_details': dumbster_details})

# company rating


def companyrate(request, id):
    user_id = request.session['id']
    dis = Customer.objects.get(id=user_id)
    companydetails = Company.objects.get(id=id)
    if request.method == 'POST':
        rate = request.POST.get('rate')
        msg = request.POST.get('feedback')
        ob = Rate()
        ob.userid = dis
        ob.companyid = companydetails
        ob.rate = rate
        ob.cmt = msg
        if (Rate.objects.filter(userid=dis, companyid=companydetails)).exists():
            if rate:
                Rate.objects.filter(
                    userid=dis, companyid=companydetails).update(rate=rate)
            elif msg:
                Rate.objects.filter(
                    userid=dis, companyid=companydetails).update(cmt=msg)
            else:
                Rate.objects.filter(
                    userid=dis, companyid=companydetails).update(rate=rate, cmt=msg)
            messages.success(request, 'Rating updated')
            return redirect('companydetails', id=id)
        ob.save()
        messages.success(request, 'Rating given')
    return redirect('companydetails', id=id)

# driver job details page


def jobdriverdetails(request, id):
    job_details = Driver_offer.objects.get(id=id)
    companydetails = job_details.companyid
    company_id = companydetails.id
    rating = Rate.objects.filter(companyid=companydetails)
    if 'id' in request.session:
        reqid = request.session['id']
        email = request.session['email']
        if (Customer.objects.filter(id=reqid, email=email)).exists():
            dis = Customer.objects.get(id=reqid)
            if (driver_job_application.objects.filter(userid=reqid, companyid=companydetails)).exists():
                msg = "YOU ALEREADY APPLIED FOR THIS JOB"
                return render(request, 'job_driver_details.html', {'id': reqid, 'dis': dis, 'companydetails': companydetails, 'rating': rating, 'job_details': job_details, 'msg': msg})
            else:
                return render(request, 'job_driver_details.html', {'id': reqid, 'dis': dis, 'companydetails': companydetails, 'rating': rating, 'job_details': job_details})
        elif (Company.objects.filter(id=reqid, cemail=email)).exists():
            dis = Company.objects.get(id=reqid)
            return render(request, 'job_driver_details.html', {'id': reqid, 'dis': dis, 'rating': rating, 'companydetails': companydetails, 'job_details': job_details})
        else:
            msg = "ERROR"
            return render(request, 'error.html', {'msg': msg})
    else:
        return render(request, 'job_driver_details.html', {'companydetails': companydetails, 'companyid': company_id, 'rating': rating, 'job_details': job_details})

# employee job details page


def jobemployeedetails(request, id):
    job_details = Employee_offer.objects.get(id=id)
    companydetails = job_details.companyid
    company_id = companydetails.id
    rating = Rate.objects.filter(companyid=companydetails)
    if 'id' in request.session:
        reqid = request.session['id']
        email = request.session['email']
        if (Customer.objects.filter(id=reqid, email=email)).exists():
            dis = Customer.objects.get(id=reqid)
            if (employee_job_application.objects.filter(userid=reqid, companyid=companydetails)).exists():
                msg = "YOU ALEREADY APPLIED FOR THIS JOB"
                return render(request, 'job_employee_details.html', {'id': reqid, 'dis': dis, 'companydetails': companydetails, 'rating': rating, 'job_details': job_details, 'msg': msg})
            else:
                return render(request, 'job_employee_details.html', {'id': reqid, 'dis': dis, 'companydetails': companydetails, 'rating': rating, 'job_details': job_details})
        elif (Company.objects.filter(id=reqid, cemail=email)).exists():
            dis = Company.objects.get(id=reqid)
            return render(request, 'job_employee_details.html', {'id': reqid, 'dis': dis, 'rating': rating, 'companydetails': companydetails, 'job_details': job_details})
        else:
            msg = "ERROR"
            return render(request, 'error.html', {'msg': msg})
    else:
        return render(request, 'job_employee_details.html', {'companydetails': companydetails, 'companyid': company_id, 'rating': rating, 'job_details': job_details})

# driver job application page


def applicationjobdriverpage(request, id):
    reqid = request.session['id']
    dis = Customer.objects.get(id=reqid)
    job = Driver_offer.objects.get(id=id)
    company = Company.objects.get(cname=job.companyid)
    return render(request, 'apply_jobdriver.html', {'dis': dis, 'job': job, 'company': company})

# driver job application


def applicationjobdriver(request, id):
    reqid = request.session['id']
    dis = Customer.objects.get(id=reqid)
    job = Driver_offer.objects.get(id=id)
    company = Company.objects.get(cname=job.companyid)
    if request.method == "POST":
        exp = request.POST.get('expirence')
        license = request.FILES['licence']
        ob = driver_job_application()
        ob.userid = dis
        ob.companyid = company
        ob.jobid = job
        ob.phone = dis.phone
        ob.exp = exp
        ob.limg = license
        ob.status = 1
        ob.review = 0
        if (driver_job_application.objects.filter(userid=dis, companyid=company, jobid=job)).exists():
            msg = "Application Aleady Submitted 🚨"
            return render(request, 'error.html', {'msg': msg})
        html_template = 'email.html'
        email_msg = "🚨 New Job Application 🚨"
        html_message = render_to_string(
            html_template, {'uname': dis, 'email_msg': email_msg})
        subject = "🚨"+str(dis)+" Applied for driver job 🚨"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [company.cemail]
        message = EmailMessage(subject, html_message,
                               email_from, recipient_list)
        message.content_subtype = 'html'
        message.send()
        ob.save()
        messages.success(request, 'Application Submited Sucessfully')
        return redirect('index')
    msg = "ERROR"
    return render(request, 'error.html', {'msg': msg})

# employee job application page


def applicationjobemployeepage(request, id):
    reqid = request.session['id']
    dis = Customer.objects.get(id=reqid)
    job = Employee_offer.objects.get(id=id)
    company = Company.objects.get(cname=job.companyid)
    return render(request, 'apply_jobemployee.html', {'dis': dis, 'job': job, 'company': company})

# employee job application


def applicationjobemployee(request, id):
    reqid = request.session['id']
    dis = Customer.objects.get(id=reqid)
    job = Employee_offer.objects.get(id=id)
    company = Company.objects.get(cname=job.companyid)
    if request.method == "POST":
        ob = employee_job_application()
        ob.userid = dis
        ob.companyid = company
        cid = Company.objects.get(cname=job)
        jid = Driver_offer.objects.get(companyid=cid)
        ob.jobid = jid
        ob.phone = dis.phone
        ob.status = 1
        ob.review = 0
        if (employee_job_application.objects.filter(userid=dis, companyid=company, jobid=jid)).exists():
            msg = "Application Aleady Submitted!"
            return render(request, 'error.html', {'msg': msg})
        html_template = 'email.html'
        email_msg = "🚨 New Job Application 🚨"
        html_message = render_to_string(
            html_template, {'uname': dis, 'email_msg': email_msg})
        subject = "🚨"+str(dis)+" Applied for Employee job 🚨"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [company.cemail]
        message = EmailMessage(subject, html_message,
                               email_from, recipient_list)
        message.content_subtype = 'html'
        message.send()
        ob.save()
        ob.save()
        messages.success(request, 'Application Submited Sucessfully')
        return redirect('index')
    msg = "ERROR"
    return render(request, 'error.html', {'msg': msg})

# driver job details page from notification


def jobdriverdetails_notification(request, id):
    job = driver_job_application.objects.get(id=id)
    x = job.companyid
    job_details = Driver_offer.objects.get(companyid=x)
    companydetails = job_details.companyid
    company_id = companydetails.id
    rating = Rate.objects.filter(companyid=companydetails)
    if 'id' in request.session:
        reqid = request.session['id']
        email = request.session['email']
        if (Customer.objects.filter(id=reqid, email=email)).exists():
            dis = Customer.objects.get(id=reqid)
            return render(request, 'job_driver_details.html', {'id': reqid, 'dis': dis, 'companydetails': companydetails, 'rating': rating, 'job_details': job_details})
        elif (Company.objects.filter(id=reqid, cemail=email)).exists():
            dis = Company.objects.get(id=reqid)
            return render(request, 'job_driver_details.html', {'id': reqid, 'dis': dis, 'rating': rating, 'companydetails': companydetails, 'job_details': job_details})
        else:
            msg = "ERROR"
            return render(request, 'error.html', {'msg': msg})
    else:
        return render(request, 'job_driver_details.html', {'companydetails': companydetails, 'companyid': company_id, 'rating': rating, 'job_details': job_details})

# employee job details page from notification


def jobemployeedetails_notification(request, id):
    job = employee_job_application.objects.get(id=id)
    x = job.jobid
    cid = Company.objects.get(cname=x)
    job_details = Employee_offer.objects.get(companyid=cid)
    companydetails = job_details.companyid
    company_id = companydetails.id
    rating = Rate.objects.filter(companyid=companydetails)
    if 'id' in request.session:
        reqid = request.session['id']
        email = request.session['email']
        if (Customer.objects.filter(id=reqid, email=email)).exists():
            dis = Customer.objects.get(id=reqid)
            return render(request, 'job_employee_details.html', {'id': reqid, 'dis': dis, 'companydetails': companydetails, 'rating': rating, 'job_details': job_details})
        elif (Company.objects.filter(id=reqid, cemail=email)).exists():
            dis = Company.objects.get(id=reqid)
            return render(request, 'job_employee_details.html', {'id': reqid, 'dis': dis, 'rating': rating, 'companydetails': companydetails, 'job_details': job_details})
        else:
            msg = "ERROR"
            return render(request, 'error.html', {'msg': msg})
    else:
        return render(request, 'job_employee_details.html', {'companydetails': companydetails, 'companyid': company_id, 'rating': rating, 'job_details': job_details})

# company details from offer accept notification


def companydetails_from_accept_notification(request, cname):
    companydetails = Company.objects.get(cname=cname)
    company_id = companydetails.id
    rating = Rate.objects.filter(companyid=companydetails)
    driver_details = Driver_offer.objects.filter(
        vacancy__gt=0, companyid=companydetails)
    employee_details = Employee_offer.objects.filter(
        vacancy__gt=0, companyid=companydetails)
    dumbster_details = Dumbster.objects.get(companyid=companydetails, status=1)
    if 'id' in request.session:
        reqid = request.session['id']
        email = request.session['email']
        if (Customer.objects.filter(id=reqid, email=email)).exists():
            dis = Customer.objects.get(id=reqid)
            return render(request, 'company_details.html', {'id': reqid, 'dis': dis, 'companydetails': companydetails, 'rating': rating, 'driver_details': driver_details, 'employee_details': employee_details, 'dumbster_details': dumbster_details})
        elif (Company.objects.filter(id=reqid, cemail=email)).exists():
            dis = Company.objects.get(id=reqid)
            return render(request, 'company_details.html', {'id': reqid, 'dis': dis, 'companydetails': companydetails, 'rating': rating, 'driver_details': driver_details, 'employee_details': employee_details, 'dumbster_details': dumbster_details})
    else:
        return render(request, 'company_details.html', {'companydetails': companydetails, 'rating': rating, 'driver_details': driver_details, 'employee_details': employee_details, 'dumbster_details': dumbster_details})
    msg = "ERROR"
    return render(request, 'error.html', {'msg': msg})

# customer offer accept


def offer_accept(request, cname, role):
    id = request.session['id']
    dis = Customer.objects.get(id=id)
    companydetails = Company.objects.get(cname=cname)
    Employee.objects.filter(
        userid=dis, companyid=companydetails, role=role).update(status=1)
    Customer.objects.filter(name=dis, status=1).update(status=0)
    if role == "driver":
        driver_job_application.objects.filter(
            userid=dis, companyid=companydetails).update(status=0)
        x = Driver_offer.objects.get(companyid=companydetails)
        vac = x.vacancy
        m = vac-1
        Driver_offer.objects.filter(companyid=companydetails).update(vacancy=m)
        if (job_assigned.objects.filter(companyid=companydetails, employeeid="")).exists():
            job = job_assigned.objects.filter(
                companyid=companydetails, employeeid="")
            for i in job:
                job_assigned.objects.filter(companyid=companydetails, employeeid="", job_id=i.job_id).update(
                    employeeid=dis.name, employeephone=dis.phone)
    elif role == "worker":
        employee_job_application.objects.filter(
            userid=dis, companyid=companydetails).update(status=0)
        x = Employee_offer.objects.get(companyid=companydetails)
        vac = x.vacancy
        m = vac-1
        Employee_offer.objects.filter(
            companyid=companydetails).update(vacancy=m)
    return redirect('signin')

# customer offer deny


def offer_deny(request, cname, role):
    id = request.session['id']
    dis = Customer.objects.get(id=id)
    companydetails = Company.objects.get(cname=cname)
    Employee.objects.filter(
        userid=dis, companyid=companydetails, role=role).delete()
    Customer.objects.filter(name=dis, status=0).update(status=1)
    if role == "driver":
        x = Driver_offer.objects.get(companyid=companydetails)
        vac = x.vacancy
        m = vac+1
        Driver_offer.objects.filter(companyid=companydetails).update(vacancy=m)
        driver_job_application.objects.filter(
            userid=dis, companyid=companydetails).delete()
    elif role == "worker":
        x = Employee_offer.objects.get(companyid=companydetails)
        vac = x.vacancy
        m = vac+1
        Employee_offer.objects.filter(
            companyid=companydetails).update(vacancy=m)
        employee_job_application.objects.filter(
            userid=dis, companyid=companydetails).delete()
    messages.success(request, 'Comapanies offer Denied')
    return redirect('index')

# service booking page


def servicebookingpage(request, id):
    uid = request.session['id']
    dis = Customer.objects.get(id=uid)
    companydetails = Company.objects.get(id=id)
    return render(request, 'service_booking.html', {'dis': dis, 'companydetails': companydetails})

# service booking payment page


def servicebookingpaymentpage(request, id):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    uid = request.session['id']
    dis = Customer.objects.get(id=uid)
    companydetails = Company.objects.get(id=id)
    total = companydetails.crate
    purpose = "service"
    if request.method == 'POST':
        location = request.POST.get('location')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        time = request.POST.get('time')
        date = request.POST.get('date')
        phone = request.POST.get('phone')
        if request.POST.get('latitude'):
            latitude = request.POST.get('latitude')
        else:
            latitude = ""
        if request.POST.get('longitude'):
            longitude = request.POST.get('longitude')
        else:
            longitude = ""
        if (today > date):
            msg = "Check the date.!"
            return render(request, 'error.html', {'msg': msg})
        if (service_booking.objects.filter(companyid=companydetails, date=date, time=time)).exists():
            msg = "No Service Available at this time!"
            return render(request, 'error.html', {'msg': msg})
        if (service_booking.objects.filter(userid=dis, status=1)).exists():
            msg = "You already booked a service!.Check your profile!"
            return render(request, 'error.html', {'msg': msg})
        return render(request, 'payment.html', {'dis': dis, 'companydetails': companydetails, 'location': location, 'address': address, 'pincode': pincode, 'time': time, 'date': date, 'phone': phone, 'purpose': purpose, 'total': total, 'today': today, 'latitude': latitude, 'longitude': longitude})

# payment success page


def payment_successfull(request):
    return render(request, 'payment_success.html')

# booking services of company


def servicebooking(request, id):
    msg = ""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    uid = request.session['id']
    dis = Customer.objects.get(id=uid)
    companydetails = Company.objects.get(id=id)
    Employee.objects.filter(userid=dis, companyid=companydetails)
    if request.method == "POST":
        address = request.POST.get('address')
        location = request.POST.get('location')
        pincode = request.POST.get('pincode')
        time = request.POST.get('time')
        date = request.POST.get('date')
        phone = request.POST.get('phone')
        total = request.POST.get('total')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        creadit_card = request.POST.get('creadit_card')
        expiration = request.POST.get('expiration')
        cvv = request.POST.get('cvv')
        name = request.POST.get('name')
        ob = service_booking()
        ob.userid = dis
        ob.companyid = companydetails
        ob.address = address
        ob.location = location
        ob.pincode = pincode
        ob.time = time
        ob.date = date
        ob.phone = phone
        ob.rate = total
        ob.latitude = latitude
        ob.longitude = longitude
        ob.status = 1
        ob.out_for_service = 0
        ob.arrived_near = 0
        ob.completed = 0
        if (service_booking.objects.filter(userid=dis, companyid=companydetails, status=1)).exists():
            msg = "Already Booked"
            return render(request, 'error.html', {'msg': msg})
        if (creadit_card == "5136184554683894" and expiration == "05/20" and cvv == "123" and name == "user"):
            ac = payment()
            ac.userid = dis
            ac.companyid = companydetails
            ac.is_for = "waste collecting"
            ac.date = today
            ac.rate = companydetails.crate
            ac.status = 1
            sb = job_assigned()
            sb.companyid = companydetails
            emp = Employee.objects.filter(
                companyid=companydetails, role="driver")
            if len(emp) > 0:
                employeename = random.choice(emp)
                sb.employeeid = employeename.userid
                sb.employeephone = employeename.ephone
                em = employeename.userid
            else:
                em = ""
                sb.employeeid = ""
            if (job_assigned.objects.filter(companyid=companydetails, employeeid=em, assistant__isnull=True, date=date)).exclude(assistant="NILL").exists():
                assistentname = job_assigned.objects.filter(
                    companyid=companydetails, employeeid=em, date=date).first()
                sb.assistant = assistentname.assistant
            else:
                sb.assistant = ""
            sb.dumbster_scheduled = ""
            sb.service_scheduled = dis
            sb.address = address
            sb.location = location
            sb.pincode = pincode
            sb.phone = phone
            sb.date = date
            sb.time = time
            sb.latitude = latitude
            sb.longitude = longitude
            sb.out_for_service = 0
            sb.arrived_near = 0
            sb.completed = 0
            sb.status = 1
            data = {
                'user': dis,
                'companydetails': companydetails,
                'total': total,
                'today': today,
                'phone': phone,
                'address': address,
                'location': location,
                'pincode': pincode,
                'date': date,
                'time': time,
                'service': '1'
            }
            template = get_template('payment_bill.html')
            html = template.render(data)
            result = BytesIO()
            # , link_callback=fetch_resources)
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
            pdf = result.getvalue()
            filename = 'payment_bill_' + str(dis) + '.pdf'
            html_template = 'email.html'
            email_msg = "🌟" + str(companydetails)+"🚨"+" Service Booked ♻"
            html_message = render_to_string(
                html_template, {'uname': dis, 'email_msg': email_msg})
            subject = '🎊 Thank You for booking our service 🌟'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [dis.email]
            message = EmailMessage(subject, html_message,
                                   email_from, recipient_list)
            message.content_subtype = 'html'
            message.attach(filename, pdf, 'application/pdf')
            message.send()
            ob.save()
            ac.save()
            sb.save()
            return render(request, 'payment_success.html')
        else:
            msg = "Card Deatils...ERROR!"
            return render(request, 'error.html', {'msg': msg})
    msg = "ERROR"
    return render(request, 'error.html', {'msg': msg})

# dumbster booking page


def bookdumbsterpage(request, cname):
    uid = request.session['id']
    dis = Customer.objects.get(id=uid)
    companydetails = Company.objects.get(cname=cname)
    dumbsterdetails = Dumbster.objects.get(companyid=companydetails, status=1)
    return render(request, 'book_dumbster.html', {'dis': dis, 'dumbsterdetails': dumbsterdetails})

# dumbster booking page


def bookdumbsterpaymentpage(request, cid):
    msg = ""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    uid = request.session['id']
    dis = Customer.objects.get(id=uid)
    companydetails = Company.objects.get(cname=cid)
    dumbsterdetails = Dumbster.objects.get(companyid=companydetails, status=1)
    if request.method == 'POST':
        numberofdumbster = request.POST.get('number')
        numberofday = request.POST.get('day')
        rate = request.POST.get('rate')
        size = request.POST.get('size')
        date = request.POST.get('date')
        location = request.POST.get('location')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        phone = request.POST.get('phone')
        total = int(numberofday)*int(rate)
        purpose = "dumbster"
        if (dumbsterdetails.number < numberofdumbster):
            msg = "This much Dumbster is not available"
            return render(request, 'error.html', {'msg': msg})
        return render(request, 'payment.html', {'dis': dis, 'companydetails': companydetails, 'phone': phone, 'location': location, 'address': address, 'pincode': pincode, 'dumbsterdetails': dumbsterdetails, 'numberofdumbster': numberofdumbster, 'rate': rate, 'size': size, 'today': today, 'numberofday': numberofday, 'total': total, 'purpose': purpose, 'date': date, 'latitude': latitude, 'longitude': longitude})
    msg = "ERROR"
    return render(request, 'error.html', {'msg': msg})

# dumbster booking section


def bookdumbster(request, cid):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    msg = ""
    uid = request.session['id']
    dis = Customer.objects.get(id=uid)
    companydetails = Company.objects.get(cname=cid)
    dumbsterdetails = Dumbster.objects.get(companyid=companydetails, status=1)
    if request.method == 'POST':
        numberofdumbster = request.POST.get('number')
        numberofday = request.POST.get('day')
        rate = request.POST.get('rate')
        size = request.POST.get('size')
        date = request.POST.get('date')
        location = request.POST.get('location')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        creadit_card = request.POST.get('creadit_card')
        expiration = request.POST.get('expiration')
        cvv = request.POST.get('cvv')
        name = request.POST.get('name')
        ob = dumbster_booking()
        ob.userid = dis
        ob.companyid = companydetails
        ob.dumbsterid = dumbsterdetails
        ob.numberofdumbster = numberofdumbster
        ob.address = dis.address
        ob.location = dis.location
        ob.pincode = dis.pincode
        ob.date = date
        ob.location = location
        ob.address = address
        ob.pincode = pincode
        ob.phone = phone
        ob.numberofday = numberofday
        no = int(numberofday)
        date1 = date
        dd = datetime.datetime.strptime(date1, "%Y-%m-%d").date()
        ds = dd+timedelta(days=no)
        ob.expire_date = ds
        ob.rate = rate
        ob.size = size
        ob.latitude = latitude
        ob.longitude = longitude
        ob.out_for_service = 0
        ob.arrived_near = 0
        ob.completed = 0
        ob.status = 1
        if (dumbster_booking.objects.filter(userid=dis, companyid=companydetails, status=1)).exists():
            msg = "Already Booked"
            return render(request, 'error.html', {'msg': msg})
        if (creadit_card == "5136184554683894" and expiration == "05/20" and cvv == "123" and name == "user"):
            ac = payment()
            ac.userid = dis
            ac.companyid = companydetails
            ac.is_for = "dumbster rental"
            ac.date = today
            ac.rate = rate
            ac.status = 1
            x = Dumbster.objects.get(companyid=companydetails, status=1)
            m = int(x.number)
            n = int(numberofdumbster)
            v = m-n
            Dumbster.objects.filter(
                companyid=companydetails, status=1).update(number=v)
            db = job_assigned()
            db.companyid = companydetails
            emp = Employee.objects.filter(
                companyid=companydetails, role="driver")
            if len(emp) > 0:
                employeename = random.choice(emp)
                db.employeeid = employeename.userid
                db.employeephone = employeename.ephone
                em = employeename.userid
            else:
                em = ""
                db.employeeid = ""
            if (job_assigned.objects.filter(companyid=companydetails, employeeid=em, assistant__isnull=True, date=date)).exclude(assistant="NILL").exists():
                assistentname = job_assigned.objects.filter(
                    companyid=companydetails, employeeid=em, date=date).first()
                db.assistant = assistentname.assistant
            else:
                db.assistant = ""
            db.dumbster_scheduled = dis
            db.service_scheduled = ""
            db.address = address
            db.location = location
            db.pincode = pincode
            db.phone = phone
            db.date = date
            db.time = ""
            db.latitude = latitude
            db.longitude = longitude
            db.out_for_service = 0
            db.arrived_near = 0
            db.completed = 0
            db.recollect_dumbster = 0
            db.status = 1
            # expire date job assign
            ex = job_assigned()
            ex.companyid = companydetails
            emp = Employee.objects.filter(
                companyid=companydetails, role="driver")
            if len(emp) > 0:
                employeename = random.choice(emp)
                ex.employeeid = employeename.userid
                ex.employeephone = employeename.ephone
                em = employeename.userid
            else:
                em = ""
                ex.employeeid = ""
            if (job_assigned.objects.filter(companyid=companydetails, employeeid=em, date=date)).exists():
                assistent = job_assigned.objects.filter(
                    companyid=companydetails, employeeid=em, date=date)
                assistentname = assistent.first()
                ex.assistant = assistentname.assistant
            else:
                ex.assistant = ""
            ex.dumbster_scheduled = dis
            ex.service_scheduled = ""
            ex.date = ds
            ex.time = ""
            ex.latitude = latitude
            ex.longitude = longitude
            ex.address = address
            ex.location = location
            ex.pincode = pincode
            ex.phone = phone
            ex.out_for_service = 0
            ex.arrived_near = 0
            ex.completed = 0
            ex.recollect_dumbster = 1
            ex.status = 1
            data = {
                'user': dis,
                'companydetails': companydetails,
                'total': rate,
                'today': today,
                'phone': phone,
                'address': address,
                'location': location,
                'pincode': pincode,
                'date': date,
                'service': '2'
            }
            template = get_template('payment_bill.html')
            html = template.render(data)
            result = BytesIO()
            # , link_callback=fetch_resources)
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
            pdf = result.getvalue()
            filename = 'payment_bill_' + str(dis) + '.pdf'
            html_template = 'email.html'
            html_template = 'email.html'
            email_msg = "🎊"+str(companydetails)+"🚧"+"Dumpster Rented  ♻"
            html_message = render_to_string(
                html_template, {'uname': dis, 'email_msg': email_msg})
            subject = '🚧 Dumpster rented successfully 🌟'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [dis.email]
            message = EmailMessage(subject, html_message,
                                   email_from, recipient_list)
            message.content_subtype = 'html'
            message.attach(filename, pdf, 'application/pdf')
            message.send()
            ob.save()
            ac.save()
            db.save()
            ex.save()
            return render(request, 'payment_success.html')
        else:
            msg = "Details Error"
            return render(request, 'error.html', {'msg': msg})
    msg = "ERROR"
    return render(request, 'error.html', {'msg': msg})

# Search Result


def search(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        msg = " "
        company_details = Company.objects.filter(
            clocation__icontains=data, status=1)
        job_driver = Driver_offer.objects.filter(status=1)
        job_employee = Employee_offer.objects.filter(status=1)
        dumbster_details = Dumbster.objects.filter(status=1)
        if (Company.objects.filter(clocation__icontains=data, status=1)).exists():
            company_details = Company.objects.filter(
                clocation__icontains=data, status=1)
        elif (Company.objects.filter(cname__icontains=data, status=1)).exists():
            company_details = Company.objects.filter(
                cname__icontains=data, status=1)
        elif (Company.objects.filter(cpincode__icontains=data, status=1)).exists():
            company_details = Company.objects.filter(
                cpincode__icontains=data, status=1)
        else:
            msg = " Result not found "

        if 'id' in request.session:
            id = request.session['id']
            email = request.session['email']
            if (Customer.objects.filter(id=id, email=email)).exists():
                dis = Customer.objects.get(id=id)
                req_accepted = Employee.objects.filter(userid=dis)
                driver_job_applied = driver_job_application.objects.filter(
                    userid=dis)
                employee_job_applied = employee_job_application.objects.filter(
                    userid=dis)
                service_booked = service_booking.objects.filter(userid=dis)
                dumbster_booked = dumbster_booking.objects.filter(
                    userid=dis, status=1)
                if msg == " ":
                    return render(request, 'searchresult.html', {'id': id, 'dis': dis, 'company_details': company_details, 'job_driver': job_driver, 'job_employee': job_employee, 'driver_job_applied': driver_job_applied, 'employee_job_applied': employee_job_applied, 'req_accepted': req_accepted, 'service_booked': service_booked, 'dumbster_details': dumbster_details, 'dumbster_booked': dumbster_booked})
                else:
                    return render(request, 'searchresult.html', {'id': id, 'dis': dis, 'company_details': company_details, 'job_driver': job_driver, 'job_employee': job_employee, 'driver_job_applied': driver_job_applied, 'employee_job_applied': employee_job_applied, 'req_accepted': req_accepted, 'service_booked': service_booked, 'dumbster_details': dumbster_details, 'dumbster_booked': dumbster_booked, 'msg': msg})
            elif (Company.objects.filter(id=id, cemail=email)).exists():
                dis = Company.objects.get(id=id)
                driver_job_applied = driver_job_application.objects.filter(
                    companyid=dis)
                employee_job_applied = employee_job_application.objects.filter(
                    companyid=dis)
                offer_accept = Employee.objects.filter(companyid=dis, status=1)
                dumbster_booked = dumbster_booking.objects.filter(
                    companyid=dis, status=1)
                if msg == " ":
                    return render(request, 'searchresult.html', {'id': id, 'dis': dis, 'company_details': company_details, 'job_driver': job_driver, 'job_employee': job_employee, 'driver_job_applied': driver_job_applied, 'employee_job_applied': employee_job_applied, 'offer_accept': offer_accept, 'dumbster_details': dumbster_details, 'dumbster_booked': dumbster_booked})
                else:
                    return render(request, 'searchresult.html', {'id': id, 'dis': dis, 'company_details': company_details, 'job_driver': job_driver, 'job_employee': job_employee, 'driver_job_applied': driver_job_applied, 'employee_job_applied': employee_job_applied, 'offer_accept': offer_accept, 'dumbster_details': dumbster_details, 'dumbster_booked': dumbster_booked, 'msg': msg})
        else:
            if msg == " ":
                return render(request, 'searchresult.html', {'company_details': company_details})
            else:
                return render(request, 'searchresult.html', {'company_details': company_details, 'msg': msg})
        if msg == " ":
            return render(request, 'index.html', {'company_details': company_details, 'job_driver': job_driver, 'job_employee': job_employee, 'dumbster_details': dumbster_details})
        else:
            return render(request, 'index.html', {'company_details': company_details, 'job_driver': job_driver, 'job_employee': job_employee, 'dumbster_details': dumbster_details, 'msg': msg})

# booked service cancelation


def service_cancel(request, id):
    uid = request.session['id']
    dis = Customer.objects.get(id=uid)
    servicedetails = service_booking.objects.get(id=id)
    companydetails = Company.objects.get(cname=servicedetails.companyid)
    if (service_booking.objects.filter(id=id, status=1)).exists():
        service_booking.objects.get(id=id).delete()
        payment.objects.filter(userid=dis, companyid=companydetails,
                               is_for="waste collecting", status=1).delete()
        job_assigned.objects.filter(service_scheduled=dis, companyid=companydetails,
                                    date=servicedetails.date, time=servicedetails.time, status=1).delete()
        return redirect('profile')
    else:
        msg = "Contact the Company"
        return render(request, 'error.html', {'msg': msg})

# Dumbster Rental cancelation


def cancel_renteddumbster(request, id):
    uid = request.session['id']
    dis = Customer.objects.get(id=uid)
    dumbster_details = dumbster_booking.objects.get(id=id)
    companydetails = Company.objects.get(cname=dumbster_details.companyid)
    if (dumbster_booking.objects.filter(id=id, status=1)).exists():
        dumbster_booking.objects.get(id=id).delete()
        payment.objects.filter(
            userid=dis, companyid=companydetails, is_for="dumbster rental", status=1).delete()
        job_assigned.objects.filter(
            dumbster_details=dis, companyid=companydetails, date=dumbster_details.date, status=1).delete()
        job_assigned.objects.filter(dumbster_details=dis, companyid=companydetails,
                                    date=dumbster_details.expire_date, status=1).delete()
        return redirect('profile')
    else:
        msg = "Contact the Company"
        return render(request, 'error.html', {'msg': msg})

# Tracking page


def tracking_page(request):
    uid = request.session['id']
    if (Customer.objects.filter(id=uid)).exists():
        dis = Customer.objects.get(id=uid)
    elif (Employee.objects.filter(id=uid)).exists():
        emp = Employee.objects.get(id=uid)
        dis = Customer.objects.get(name=emp.userid)
    employee_details = Employee.objects.all()
    job_dumbster = ""
    job_service = ""
    dumbsteremployeedetails = ""
    serviceemployeedetails = ""
    servicedetails = service_booking.objects.filter(
        userid=dis).order_by('date')
    dumbster_details = dumbster_booking.objects.filter(
        userid=dis).order_by('date')
    context = {
        "company": Company.objects.filter(status=1),
    }
    if (job_assigned.objects.filter(dumbster_scheduled=dis)).exists():
        job_dumbster = job_assigned.objects.filter(dumbster_scheduled=dis)
        dumbsteremployeedetails = []
        for i in job_dumbster:
            if (i.employeeid == ""):
                dumbsteremployeedetails = ""
            else:
                customer = Customer.objects.get(name=i.employeeid)
                employees = Employee.objects.filter(userid=customer)
                for employee in employees:
                    dumbsteremployeedetails.append(employee.userid)
    if (job_assigned.objects.filter(service_scheduled=dis)).exists():
        job_service = job_assigned.objects.filter(service_scheduled=dis)
        for i in job_service:
            if (i.employeeid == ""):
                serviceemployeedetails = ""
            else:
                customer = Customer.objects.get(name=i.employeeid)
                serviceemployeedetails = Employee.objects.filter(
                    userid=customer)
    return render(request, 'tracking.html', {'dis': dis, 'servicedetails': servicedetails, 'dumbster_details': dumbster_details, 'job_dumbster': job_dumbster, 'job_service': job_service, 'employee_details': employee_details, 'dumbsteremployeedetails': dumbsteremployeedetails, 'serviceemployeedetails': serviceemployeedetails, 'context': context})

# help page


def help_page(request):
    return render(request, 'help.html')

# dumpster feedback after delivery completed


def dumpster_delivery_feedback(request, id):
    if request.method == "POST":
        feedback = request.POST.get('feedbackInput')
        dumbster_booking.objects.filter(id=id).update(feedback=feedback)
        messages.success(request, "Feedback send successfuly")
    return redirect('tracking_page')


#  service feedback after delivery completed

def service_delivery_feedback(request, id):
    if request.method == "POST":
        feedback = request.POST.get('feedbackInput')
        service_booking.objects.filter(id=id).update(feedback=feedback)
        messages.success(request, "Feedback send successfuly")
    return redirect('tracking_page')
