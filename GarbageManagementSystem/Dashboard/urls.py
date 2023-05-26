from django.urls import path
from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('profile/', profile,name='profile'),
    path('customerprofileupdate/', customerprofileupdate,name='customerprofileupdate'),
    path('companyprofileupdate/', companyprofileupdate,name='companyprofileupdate'),
    path('cancel_job_driver/<id>', cancel_job_driver,name='cancel_job_driver'),
    path('cancel_vehicle/<id>', cancel_vehicle,name='cancel_vehicle'),
    path('makeavailable_vehicle/<id>', makeavailable_vehicle,name='makeavailable_vehicle'),
    path('profile_jobapplications/', profile_jobapplications,name='profile_jobapplications'),
    path('profile_addvehicle/', profile_addvehicle,name='profile_addvehicle'),
    path('profile_bookingdetails/', profile_bookingdetails,name='profile_bookingdetails'),
    path('profile_jobdetails/', profile_jobdetails,name='profile_jobdetails'),
    path('employee_manager/', employee_manager,name='employee_manager'),
    path('jobdriver_req_cancel/<id>', jobdriver_req_cancel,name='jobdriver_req_cancel'),
    path('jobemployee_req_cancel/<id>', jobemployee_req_cancel,name='jobemployee_req_cancel'),
    path('profile_dumbstermanager/', profile_dumbstermanager,name='profile_dumbstermanager'),
    path('cancel_job_worker/<id>', cancel_job_worker,name='cancel_job_worker'),
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)