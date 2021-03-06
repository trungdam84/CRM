from django.urls import path
from django.conf.urls import url
from .views import customer_appointment_cancel, logoff_customer, not_customer, get_customer_api, delete_smss, appointments_json, read_smss , push_callerID, test_login, template_app_time_check, template_app_date_check ,customer_search ,get_customer, callerID, add_locker, services, boxes, appointments, customers, customer_create, appointment_create, appoinment_update, customer_delete ,customer_update, box_check, clean_boxs, appointments_view


urlpatterns = [
    path('boxes/', boxes, name='boxes'),
    path('boxes/add', add_locker, name='add-boxes'),
    path('boxes/clean', clean_boxs, name='clean-boxes'),
    path('boxes/check/<int:pk>/', box_check, name='check-box'),
    path('customers/', customers, name='customers'),
    path('', appointments, name='appointments'),
    path('customers/create/', customer_create, name='create-customer'),
    path('customers/update/<int:pk>/', customer_update, name='update-customer'),
    path('customers/delete/<int:pk>/', customer_delete, name='delete-customer'),
    path('appointment/create/', appointment_create, name='create-appointment'),
    path('appointment/update/<int:pk>/', appoinment_update, name='update-appointment'),
    path('appointments/view/', appointments_view, name='view-appointments'),
    path('appointments/json/', appointments_json, name='appointments-json'),
    path('services/', services, name='services'),
    path('callerid/', callerID, name='callerid'),
    path('push_callerid/', push_callerID, name='push-callerid'),
    path('get-customer/', get_customer, name='get-customer'),
    path('get-customer-api/', get_customer_api, name='get-customer-api'),
    path('customer_search/', customer_search, name='customer-search'),
    path('read_smss/', read_smss, name='read-smss'),
    path('delete-smss/', delete_smss, name='delete-smss'),
    path('not-customer/', not_customer, name='not-customer'),
    path('logoff-customer/', logoff_customer, name='logoff-customer'),
    path('appointment/cancel/<int:pk>/', customer_appointment_cancel, name='customer-cancel-appointment'),

    


    # path('test-login/', test_login, name='test-login'),


    



]