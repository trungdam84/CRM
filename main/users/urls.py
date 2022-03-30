from django.urls import path, include
from django.conf.urls import url
from .views import salon_admin, salon_account



urlpatterns = [

    path('admin/', salon_admin, name='salon-admin'),
    path('salon-account/', salon_account, name='salon-account'),
    # path('', include('django.contrib.auth.urls')),


    
    # path('create/', account_create, name='account-create'),
    # path('boxes/add', add_locker, name='add-boxes'),
    # path('boxes/clean', clean_boxs, name='clean-boxes'),
    # path('boxes/check/<int:pk>/', box_check, name='check-box'),
    # path('customers/', customers, name='customers'),
    # path('', appointments, name='appointments'),
    # path('customers/create/', customer_create, name='create-customer'),
    # path('customers/update/<int:pk>/', customer_update, name='update-customer'),
    # path('customers/delete/<int:pk>/', customer_delete, name='delete-customer'),
    # path('appoitment/create/', appointment_create, name='create-appointment'),
    # # path('appoitment/update/<int:pk>/', Appointment_UpdateView.as_view(), name='update-appointment'),
    # path('appoitment/update/<int:pk>/', appoinment_update, name='cancel-appointment'),
    # path('appoitment/view/', appointments_view, name='view-appointments'),
    # # url(r'^appoitment/create/(?P<>\d+)/$', appointment_create, name="create-appointment")
    # path('services/', services, name='services'),



]