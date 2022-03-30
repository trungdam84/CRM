from django.urls import path
from django.conf.urls import url
from .views import read_smss, send_ussd


urlpatterns = [
    path('read-smss/', read_smss, name='read-smss'),
    path('send-ussd/', send_ussd, name='send-ussd'),

]