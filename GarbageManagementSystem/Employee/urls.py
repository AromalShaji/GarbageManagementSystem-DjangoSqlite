from django.urls import path
from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
        path('update_out_of_service/<jid>',update_out_of_service,name='update_out_of_service'),
        path('update_arrived_near/<jid>',update_arrived_near,name='update_arrived_near'),
        path('update_completed/<jid>',update_completed,name='update_completed'),
        path('employee_leave/',employee_leave,name='employee_leave'),
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)