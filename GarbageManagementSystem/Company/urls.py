from django.urls import path
from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[  
    path('addcompanypage/', addcompanypage,name='addcompanypage'),
    path('regjobdriverpage/', regjobdriverpage,name='regjobdriverpage'),
    path('regjob_driver/', regjob_driver,name='regjob_driver'),
    path('regjobemployeepage/', regjobemployeepage,name='regjobemployeepage'),
    path('regjob_employee/', regjob_employee,name='regjob_employee'),
    path('reg_vehicle/', reg_vehicle,name='reg_vehicle'),
    path('driver_job_accept/<str:vid>/<str:uname>', driver_job_accept,name='driver_job_accept'),
    path('employee_job_accept/<str:vid>/<str:uname>', employee_job_accept,name='employee_job_accept'),
    path('adddumbsterpage/', adddumbsterpage,name='adddumbsterpage'),
    path('adddumbster/', adddumbster,name='adddumbster'),
    path('driverjob_application_reject/<str:uname>', driverjob_application_reject,name='driverjob_application_reject'),
    path('employeejob_application_reject/<str:uname>', employeejob_application_reject,name='employeejob_application_reject'),
    path('dumbster_availablity/', dumbster_availablity,name='dumbster_availablity'),
    path('dumbster_update/', dumbster_update,name='dumbster_update'),
    path('jobdriverdetails_update/', jobdriverdetails_update,name='jobdriverdetails_update'),
    path('jobemployeedetails_update/', jobemployeedetails_update,name='jobemployeedetails_update'),
    path('remove_employee/<str:ename>/<str:eemail>', remove_employee,name='remove_employee'),
    path('add_employeepage/', add_employeepage,name='add_employeepage'),
    path('addemployee_details/', addemployee_details,name='addemployee_details'),
    path('addemployee/', addemployee,name='addemployee'),
    path('remove_addemployee/<str:name>/<str:email>/<str:password>', remove_addemployee,name='remove_addemployee'),
    path('make_employee_unavailable/<str:name>/<str:email>/<str:role>', make_employee_unavailable,name='make_employee_unavailable'),
    path('assign_job/', assign_job,name='assign_job'),
    path('update_assign_job/<id>', update_assign_job,name='update_assign_job'),
    path('leave_application_approve/<id>', leave_application_approve,name='leave_application_approve'),
    path('leave_application_reject/<id>', leave_application_reject,name='leave_application_reject'),
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)