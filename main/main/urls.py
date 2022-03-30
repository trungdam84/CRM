"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from customers.views import index
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from customers.views import template_app_time_check, template_app_date_check, appointment_cancel, waitting_list_succeed, verify, appointment_confirm, appointment_succeed, callerID, unverified, otp_resend, short_appointments, waiting_list_times
from users.views import login, privacy_policy, terms_conditions, CusLoginView
from django.conf.urls import url
from django.contrib.auth.views import LogoutView


print(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
print(settings.STATIC_ROOT)
print(staticfiles_urlpatterns())
urlpatterns = [

    path('admin/', admin.site.urls),
    path('api/', include('users.urls_api')),
    path('staff/', include('customers.urls')),
    path('account/', include('users.urls')),
    path('inventory/', include('inventory.urls')),
    path('', index, name='index'),
    path('verify/', verify, name='verify'),
    path('unverified/', unverified, name='unverified'),
    path('appointment-confirm/', appointment_confirm, name='appointment_confirm'),
    path('appointment-cancel/', appointment_cancel, name='appointment_cancel'),
    path('appointment-succeed/', appointment_succeed, name='appointment_succeed'),
    path('waitting-list-succeed/', waitting_list_succeed, name='waitting-list-succeed'),
    path('waiting-list-times/', waiting_list_times, name='waiting-list-times'),
    path('caller-id/', callerID, name='caller_id'),
    path('otp-resend/', otp_resend, name='otp_resend'),
    path('short-appointments/', short_appointments, name='short-appointments'),
    path('privacy-policy/', privacy_policy, name='privacy-policy'),
    path('terms-conditions/', terms_conditions, name='terms-conditions'),
    path('app-date-check/', template_app_date_check, name='app-date-check'),
    path('app-time-check/', template_app_time_check, name='app-time-check'),
    # url(r'^login/$', login, name='login'),
    url(r'^login/$', CusLoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),  # <--
    #url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^sms/', include('sms.urls')),




]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
# + staticfiles_urlpatterns()
