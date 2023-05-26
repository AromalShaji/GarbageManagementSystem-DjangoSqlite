from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.cache import cache_control
from Home.models import Customer, Company, Rate, employee_job_application, driver_job_application, service_booking, dumbster_booking
from Company.models import Driver_offer, vehicle, Employee_offer, Dumbster
from Employee.models import Employee, job_assigned, leave
from django.contrib import messages
from datetime import datetime, date, timedelta
import datetime

# profile page


def profile(request):
    reqid = request.session['id']
    email = request.session['email']
    if (Customer.objects.filter(id=reqid, email=email)).exists():
        dis = Customer.objects.get(id=reqid)
        driver_job_applied = driver_job_application.objects.filter(userid=dis)
        employee_job_applied = employee_job_application.objects.filter(
            userid=dis)
        service_booked = service_booking.objects.filter(userid=dis)
        dumbster_booked = dumbster_booking.objects.filter(userid=dis)
        return render(request, 'profile.html', {'id': reqid, 'dis': dis, 'driver_job_applied': driver_job_applied, 'employee_job_applied': employee_job_applied, 'service_booked': service_booked, 'dumbster_booked': dumbster_booked})
    elif (Company.objects.filter(id=reqid, cemail=email)).exists():
        dis = Company.objects.get(id=reqid)
        driver_details = Driver_offer.objects.filter(companyid=dis, status=1)
        employee_details = Employee_offer.objects.filter(
            companyid=dis, status=1)
        vehicle_details = vehicle.objects.filter(companyid=dis)
        return render(request, 'profile.html', {'id': reqid, 'dis': dis, 'driver_details': driver_details, 'vehicle_details': vehicle_details, 'employee_details': employee_details})
    else:
        msg = "ERROR!"
        return render(request, 'error.html', {'msg': msg})

# customer profile details update


def customerprofileupdate(request):
    user_id = request.session['id']
    dis = Customer.objects.get(id=user_id)
    if request.method == 'POST':
        uname = request.POST.get('name')
        mail = request.POST.get('email')
        pwd = request.POST.get('password')
        phone = request.POST.get('phone')
        add = request.POST.get('address')
        lcn = request.POST.get('location')
        pc = request.POST.get('pincode')
        if (Customer.objects.filter(name=uname).exclude(id=user_id)).exists():
            msg = "User name already exist!!"
            return render(request, 'error.html', {'msg': msg})
        Customer.objects.filter(id=user_id, status=1).update(
            name=uname, email=mail, password=pwd, phone=phone, address=add, location=lcn, pincode=pc)
        messages.success(request, 'Updated')
        return redirect('profile')
    msg = "ERROR!"
    return render(request, 'error.html', {'msg': msg})

# company profile details update


def companyprofileupdate(request):
    company_id = request.session['id']
    dis = Company.objects.get(id=company_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        mail = request.POST.get('email')
        pwd = request.POST.get('password')
        phone = request.POST.get('phone')
        add = request.POST.get('address')
        lcn = request.POST.get('location')
        pc = request.POST.get('pincode')
        area = request.POST.get('pincode')
        if (Company.objects.filter(cname=name).exclude(id=company_id)).exists():
            msg = "User name already exist!!"
            return render(request, 'error.html', {'msg': msg})
        Company.objects.filter(id=company_id, status=1).update(
            cname=name, cemail=mail, cpassword=pwd, cphone=phone, caddress=add, clocation=lcn, cpincode=pc, carea=area)
        messages.success(request, 'Updated')
        return redirect('profile')
    msg = "ERROR!"
    return render(request, 'error.html', {'msg': msg})

# driver job cancelation in company profile


def cancel_job_driver(request, id):
    userid = request.session['id']
    dis = Driver_offer.objects.get(companyid=userid)
    Driver_offer.objects.filter(status=1, id=id).delete()
    messages.success(request, 'cancelled')
    return redirect('profile_jobdetails')

# employee job offer cancelation in companies profile


def cancel_job_worker(request, id):
    userid = request.session['id']
    dis = Employee_offer.objects.get(companyid=userid)
    Employee_offer.objects.filter(status=1, id=id).delete()
    messages.success(request, 'cancelled')
    return redirect('profile_jobdetails')

# make vehicle unavailable in companies profile


def cancel_vehicle(request, id):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    vehicle.objects.filter(
        status=1, id=id, companyid=companydetails).update(status=0)
    messages.success(request, 'Updated')
    return redirect('profile_addvehicle')

# make vehicle available in companies profile


def makeavailable_vehicle(request, id):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    vehicle.objects.filter(
        status=0, id=id, companyid=companydetails).update(status=1)
    messages.success(request, 'Updated')
    return redirect('profile_addvehicle')

# job applications section in profile


def profile_jobapplications(request):
    company_id = request.session['id']
    msg1 = " "
    msg2 = " "
    companydetails = Company.objects.get(id=company_id)
    employee_offer = employee_job_application.objects.filter(
        companyid=companydetails, status=1)
    driver_offer = driver_job_application.objects.filter(
        companyid=companydetails, status=1, review=0)
    driver = Employee.objects.filter(companyid=companydetails)

    if (employee_job_application.objects.filter(companyid=companydetails, status=1, review=0)).exists():
        employee_offer = employee_job_application.objects.filter(
            companyid=companydetails, status=1, review=0)
    else:
        msg2 = "No Job Applications"

    if (driver_job_application.objects.filter(companyid=companydetails, status=1, review=0)).exists():
        driver_offer = driver_job_application.objects.filter(
            companyid=companydetails, status=1, review=0)
    else:
        msg1 = "No Job Applications"
    return render(request, 'profile_job_application.html', {'id': company_id, 'companydetails': companydetails, 'employee_offer': employee_offer, 'driver_offer': driver_offer, 'driver': driver, 'msg1': msg1, 'msg2': msg2})

# add vehicle section in profile


def profile_addvehicle(request):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    employee_offer = employee_job_application.objects.filter(
        companyid=companydetails)
    driver_offer = driver_job_application.objects.filter(
        companyid=companydetails)
    vehicle_details = vehicle.objects.filter(companyid=companydetails)
    return render(request, 'profile_addvehicle.html', {'id': company_id, 'companydetails': companydetails, 'employee_offer': employee_offer, 'driver_offer': driver_offer, 'vehicle_details': vehicle_details})

# vehicle details section in profile


def profile_bookingdetails(request):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    employee_offer = employee_job_application.objects.filter(
        companyid=companydetails)
    driver_offer = driver_job_application.objects.filter(
        companyid=companydetails)
    vehicle_details = vehicle.objects.filter(companyid=companydetails)
    dumbster_booked = dumbster_booking.objects.filter(status=1)
    service_booked = service_booking.objects.filter(companyid=companydetails)
    return render(request, 'profile_bookingdetails.html', {'id': company_id, 'companydetails': companydetails, 'employee_offer': employee_offer, 'driver_offer': driver_offer, 'companydetails': companydetails, 'vehicle_details': vehicle_details, 'dumbster_booked': dumbster_booked, 'service_booked': service_booked})

# job details section in profile


def profile_jobdetails(request):
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    employee_offer = employee_job_application.objects.filter(
        companyid=companydetails)
    driver_offer = driver_job_application.objects.filter(
        companyid=companydetails)
    driver_details = Driver_offer.objects.filter(companyid=companydetails)
    employee_details = Employee_offer.objects.filter(companyid=companydetails)
    vehicle_details = vehicle.objects.filter(companyid=companydetails)
    return render(request, 'profile_jobdetails.html', {'id': company_id, 'driver_details': driver_details, 'employee_details': employee_details, 'companydetails': companydetails, 'employee_offer': employee_offer, 'driver_offer': driver_offer, 'companydetails': companydetails, 'vehicle_details': vehicle_details})

# employee manager section in profile


def employee_manager(request):
    today = datetime.datetime.now().date()
    company_id = request.session['id']
    companydetails = Company.objects.get(id=company_id)
    employee_offer = employee_job_application.objects.filter(
        companyid=companydetails)
    driver_offer = driver_job_application.objects.filter(
        companyid=companydetails)
    driver_details = Driver_offer.objects.filter(companyid=companydetails)
    vehicle_details = vehicle.objects.filter(
        companyid=companydetails, status=1)
    employee_details = Employee.objects.filter(companyid=companydetails)
    employee_driver = Employee.objects.filter(
        companyid=companydetails, role='driver', status=1)
    employee_worker = Employee.objects.filter(
        companyid=companydetails, role='worker', status=1)
    assignedjob = job_assigned.objects.filter(companyid=companydetails)
    dumbster_booked = dumbster_booking.objects.filter(
        companyid=companydetails).exclude(status=1)
    service_booked = service_booking.objects.filter(
        companyid=companydetails, status=1)
    employee_leave = leave.objects.filter(
        companyid=companydetails, status=1, approved=0, rejected=0).order_by('start_date')
    return render(request, 'profile_employee_manager.html', {'id': company_id, 'driver_details': driver_details, 'employee_details': employee_details, 'employee_worker': employee_worker, 'employee_driver': employee_driver, 'companydetails': companydetails, 'vehicle_details': vehicle_details, 'employee_details': employee_details, 'assignedjob': assignedjob, 'dumbster_booked': dumbster_booked, 'service_booked': service_booked, 'employee_leave': employee_leave, 'today': today})


# driver job request cancelation in customer profile
def jobdriver_req_cancel(request, id):
    uid = request.session['id']
    dis = Customer.objects.get(id=uid)
    jobdetails = driver_job_application.objects.get(id=id)
    companydetails = Company.objects.get(cname=jobdetails.companyid)
    if (Employee.objects.filter(userid=dis, companyid=companydetails, status=0, role="driver")).exists():
        Employee.objects.filter(
            userid=dis, companyid=companydetails, status=0, role="driver").delete()
    driver_job_application.objects.filter(
        id=id, userid=dis, companyid=companydetails).delete()
    return redirect('profile')

# employee job request cancelation in customer profile


def jobemployee_req_cancel(request, id):
    uid = request.session['id']
    dis = Customer.objects.get(id=uid)
    jobdetails = employee_job_application.objects.get(id=id)
    companydetails = Company.objects.get(cname=jobdetails.companyid)
    if (Employee.objects.filter(userid=dis, companyid=companydetails, status=0, role="worker")).exists():
        Employee.objects.filter(
            userid=dis, companyid=companydetails, status=0, role="worker").delete()
    employee_job_application.objects.filter(
        id=id, userid=dis, companyid=companydetails).delete()
    return redirect('profile')

# dumbster section in company profile


def profile_dumbstermanager(request):
    uid = request.session['id']
    dis = Company.objects.get(id=uid)
    dumbsterdetails = Dumbster.objects.filter(companyid=dis)
    dumbster_booked = dumbster_booking.objects.filter(companyid=dis)
    return render(request, 'profile_dumbster.html', {'dis': dis, 'dumbsterdetails': dumbsterdetails, 'dumbster_booked': dumbster_booked})
