from django.core.cache import cache
from django.shortcuts import render, reverse
from customers.models import AvailableTimesCache, NotTurnedUp, QueueSMS, CallerID, AppointmentStatus, SalonAccount, GenaralOpenTime, SpecialOpenTime, WeeklyCloseDay ,StoreLocker, Customer, Appointment, SalonStylist, ClosedDay, ServiceBlock, ExtraServiceBlock
from datetime import time, timedelta, date, datetime
from django.views.generic import CreateView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound, HttpResponseForbidden, response
from django.contrib import messages
import calendar, random, string
from django.contrib.auth.decorators import login_required, permission_required
import time as ostime
import threading
from users.decorators import manager_required, salon_account_check
from customers.models import TemplateAppointment
from customers.temp import TempAppointment
from pathlib import Path
import logging, os
from sms.sms_module import SMS
from django.utils import timezone
from customers.models import CustomerSession
from logs.decorators import front_end_exception_log




from django.conf import settings

logs_path = os.path.join(Path(settings.BASE_DIR).parents[0], 'logs')

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler(os.path.join(logs_path, 'customers.log'))

file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)




def cleanupTemp(appoinmentID, sleepTime=60):
    ostime.sleep(sleepTime)
    templateAppoints = TemplateAppointment.objects.filter(appoinmentID=appoinmentID)
    for templateAppoint in templateAppoints:
        if not templateAppoint.waitTo:
            templateAppoint.delete()
        elif templateAppoint.waitTo < timezone.now():
            templateAppoint.delete()


def queueMSM(salonAcc, message, destination):
    if destination.startswith('07') and destination.isdigit() and (len(destination) == 11):
        QueueSMS(salonAcc=salonAcc, message=message, destination=destination).save()

def not_customer(request):
    reqst = request

    session = CustomerSession.objects.filter(session=reqst.COOKIES['cus_session']).first()
    customer = session.customer
    customer.mobile = None
    customer.save()
    session.delete()
    rev = reverse('index')

    return HttpResponseRedirect(rev)

def logoff_customer(request):
    reqst = request

    session = CustomerSession.objects.filter(session=reqst.COOKIES['cus_session']).first()
    session.delete()
    rev = reverse('index')

    return HttpResponseRedirect(rev)

# Create your views here.

def customer_appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if 'cus_session' in request.COOKIES:
        
        try:
            session = CustomerSession.objects.filter(session=request.COOKIES['cus_session']).first()
            if session.expired > timezone.now():
                customer = session.customer
            else:
                customer = None 
        except:
            customer = None
    else:
        customer = None
    if customer != None:
        if appointment.customer == customer:
            appointment.status = 3
            appointment.save()


        return JsonResponse({"error": 0, 'message':'appointment successfully cancelled'})
    else: 
        return JsonResponse({"error": -1, 'message':'appointment unsuccessfully cancelled'})


@front_end_exception_log
def index(request):

    
    # print(reqst.META['HTTP_HOST'])
    
    print(request.COOKIES)

    reqst = request
    salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
    if 'cus_session' in reqst.COOKIES:
        
        try:
            session = CustomerSession.objects.filter(session=reqst.COOKIES['cus_session']).first()
            if session.expired > timezone.now():
                customer = session.customer
            else:
                customer = None 
        except:
            customer = None
    else:
        customer = None

    if salonAcc.frontEndAppointment:
        if reqst.method == 'POST':
            salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
            req = reqst.POST
            appoinmentMobile = req['mobile']
            appoinmentFName = req['firstname']
            appoinmentLName = req['lastname']
   
            letters = string.ascii_letters
            appoinmentID = ''.join(random.choice(letters) for i in range(25))
            letters = string.digits
            appoinmentOTP = ''.join(random.choice(letters) for i in range(4))
            templateAppoint = TemplateAppointment(appoinmentID=appoinmentID,
                                                    appoinmentFName=appoinmentFName,
                                                    appoinmentLName=appoinmentLName,
                                                    appoinmentMobile=appoinmentMobile,
                                                    appoinmentOTP=appoinmentOTP,
                                                    salonAcc=salonAcc,         
                                                    )

            templateAppoint.save()
            extras = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)
            for extra in extras:
                if extra.name in req:
                    # print(templateAppoint)
                    # print(extra)
                    templateAppoint.appoinmentEXtra.add(extra)
                    templateAppoint.save()
            t =threading.Thread(target = cleanupTemp, name = 'thread{}'.format(appoinmentID), args=(appoinmentID, 1200))
            t.daemon = True
            t.start()

            
            print(appoinmentOTP)

            message = 'This is verification message from {} Your verification code is {}.'.format(salonAcc.salonName,appoinmentOTP)
            queueMSM(salonAcc, message, appoinmentMobile)
            # context = {
            #     'appoinmentID':appoinmentID
            # }

            rev = reverse('verify')
            rev = '{}?id={}'.format(rev, appoinmentID)
            return HttpResponseRedirect(rev)
            #rev = reverse('appointment_confirm')
            #rev = '{}?id={}'.format(rev, appoinmentID)
            #return HttpResponseRedirect(rev)  

        else:
            extraservices = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)
            # print(extraservices)
            serviceblocks = ServiceBlock.objects.filter(salonAcc=salonAcc)
            context = {
                'extraservices':extraservices.all(),
                'serviceblocks':serviceblocks,
                'salonAcc':salonAcc,
                'customer':customer
            }
            # print(customer)
            if customer != None:
                appointments = Appointment.objects.filter(customer=customer)
                context['appointments'] = appointments

            return render(request, 'customers/index.html', context)
        
    else:
        extraservices = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)
        # print(extraservices)
        serviceblocks = ServiceBlock.objects.filter(salonAcc=salonAcc)


        context = {
            'extraservices':extraservices.all(),
            'serviceblocks':serviceblocks,
            'salonAcc':salonAcc
        }
        print(customer)
        if customer != None:
            appointments = Appointment.objects.filter(customer=customer)
            context['appointments'] = appointments
        return render(request, 'customers/index.html', context)


def unverified(request):
    return render(request, 'customers/unverified.html')

def otp_resend(request):
    reqst = request
    salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
    appointment = TemplateAppointment.objects.filter(appoinmentID=reqst.GET.get('id')).first()
    if not appointment:
        return JsonResponse({'error':0, 'message': 'Your session expried'})
    if (timezone.now() - appointment.createdTime <= timedelta(minutes=1)):
        return JsonResponse({'error':1, 'message': 'Please wait for few minutes befor click resend'})
    elif appointment.otpResend == None:
        message = 'This is verification message from {} Your verification code is {}.'.format(salonAcc.salonName,appointment.appoinmentOTP)
        appointment.otpResend = timezone.now()
        appointment.save()
        queueMSM(salonAcc, message, appointment.appoinmentMobile)
        return JsonResponse({'error':0, 'message': 'Verify code has been resent. If you still not recevice please call us on {}'.format(salonAcc.tel)})
    else:
        return JsonResponse({'error':0, 'message': 'Verify code has been resent. If you still not recevice please call us on {}'.format(salonAcc.tel)})

def verify(request):
    reqst = request
    # print(reqst.META['HTTP_HOST'])
    salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
    # appointment = TemplateAppointment.objects.filter(appoinmentID=reqst['appointmentID'], salonAcc=salonAcc).first()
    if reqst.method == 'POST':
        req = reqst.POST
        if 'verify' in req:
            appointment = TemplateAppointment.objects.filter(appoinmentID=req['appointmentID'], salonAcc=salonAcc).first()
            if not appointment:
                return render(request, 'customers/appoitment_timeout.html')
            if appointment.appoinmentOTP == req['otp']:
                appointment.verified = True
                appointment.save()
                rev = reverse('appointment_confirm')
                if 'remember-device' in req:
                    rev = '{}?id={}&rem={}'.format(rev, appointment.appoinmentID, '1')
                else:
                    rev = '{}?id={}&rem={}'.format(rev, appointment.appoinmentID, '0')
                return HttpResponseRedirect(rev)  

            else:
                messages.error(request, 'You have entered wrong One Time Passcode')

                context = {
                    'appointment':appointment,
                    'salonAcc':salonAcc
                }
                return render(request, 'customers/verify.html', context)
        if 'resend' in req:
                messages.error(request, 'Your Passcode has been resent')

                context = {
                    'appointment':appointment,
                    'salonAcc':salonAcc
                }
                return render(request, 'customers/verify.html', context)
    else:
        appID = request.GET.get('id')
        appointment = TemplateAppointment.objects.filter(appoinmentID=appID, salonAcc=salonAcc).first()
        if not appointment:
            return render(request, 'customers/appointment_timeout.html')
        context = {
            'appointment':appointment,
            'salonAcc':salonAcc
        }
        return render(request, 'customers/verify.html', context)




def short_appointments(request):
    reqst = request
    salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
    mobile = reqst.session['mobile']

    context = {
        'mobile':mobile,
        'salonACC':salonAcc
    }
    return render(request, 'customers/short_appointments.html', context)


def appointment_confirm(request):
    # try:
    reqst = request
    salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
    extraservices = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)

    # temp_appointment = TemplateAppointment.objects.filter(appoinmentID=reqst.GET.get('appoinmentID'), salonAcc=salonAcc).first()
    if reqst.method == "POST":

        req = reqst.POST
        service = ServiceBlock.objects.filter(pk=req["service"], salonAcc=salonAcc).first()
        temp_appointment = TemplateAppointment.objects.filter(appoinmentID=req['appoinmentID'], salonAcc=salonAcc).first()
        if not temp_appointment:
            return render(request, 'customers/appointment_timeout.html')
        if temp_appointment.verified:

            if 'waiting_submit' in req:
                temp_appointment.waitFrom = datetime.strptime('{} {}'.format(req['wait_date'], req['waitting_time_from']), '%Y-%m-%d %H:%M:%S')
                temp_appointment.waitTo = datetime.strptime('{} {}'.format(req['wait_date'], req['waitting_time_to']), '%Y-%m-%d %H:%M:%S')
                temp_appointment.save()
                rev = reverse('waitting-list-succeed')
                rev = '{}?id={}'.format(rev, req['appoinmentID'])
                return HttpResponseRedirect(rev)
            cus = Customer.objects.filter(mobile=temp_appointment.appoinmentMobile, firstName=temp_appointment.appoinmentFName, lastName=temp_appointment.appoinmentLName, salonAcc=salonAcc).first()
            if not cus:
                temp_appointment.appoinmentFName
                custm = Customer(salonAcc=salonAcc,
                        firstName=temp_appointment.appoinmentFName,
                        lastName=temp_appointment.appoinmentLName,
                        mobile=temp_appointment.appoinmentMobile,
                        )
                custm.save()
                
            else:
                custm = Customer.objects.filter(mobile=temp_appointment.appoinmentMobile, firstName=temp_appointment.appoinmentFName, lastName=temp_appointment.appoinmentLName, salonAcc=salonAcc).first()
            custms = Customer.objects.filter(mobile=temp_appointment.appoinmentMobile, salonAcc=salonAcc)
            shortappntcheck = []
            for custm in custms:
                quset = Appointment.objects.filter(dateTime__range=(timezone.now(), timezone.now() + timedelta(days=60)), customer=custm, service=service).order_by('dateTime')
                for app in quset:
                    shortappntcheck.append(app)
            logger.warning(' shortappntcheck {}'.format(shortappntcheck))
            if shortappntcheck:
                for check in shortappntcheck:
                    print(datetime.strptime(req['time'], '%Y-%m-%d %H:%M:%S'), check.dateTime)
                    if abs(datetime.strptime(req['time'], '%Y-%m-%d %H:%M:%S') - check.dateTime) <= timedelta(days=13):
                        request.session['mobile'] = temp_appointment.appoinmentMobile
                        return redirect(reverse('short-appointments'))


        

            if req['date'] in req['time']:


                apnt_time = 0

                

                appntDateTime = datetime.strptime(req['time'], "%Y-%m-%d %H:%M:%S")
                temp_appnt = TempAppointment(customer=custm,
                                            salonAcc=salonAcc,
                                            dateTime=appntDateTime,
                                            notice=req['notice'],
                                            service=service,
                                            )
                temp_appnt.temp_extras = []
                for extra in extraservices:
                    if extra.name in req:
                        temp_appnt.temp_extras.append(extra)
                if 'stylist' in req:
                    temp_appnt.stylist = SalonStylist.objects.filter(salonAcc=salonAcc, pk=req['stylist']).first()
                
                appointment = temp_appnt.save_appointment()




                # print(resp)
                if appointment:
                    # appointment = resp['message']
                    extraservicestr = ''
                    for extra in appointment.extras.all():
                        extraservicestr += (extra.name + ' ')
                if appointment.customer.mobile:
                    cancel_mes = 'To cancel go to. https://{}/appointment-cancel/?id={}'.format(salonAcc.website, appointment.cancelID)
                    message = '{}: Your appointment at {} has been successfully booked. {}'.format(salonAcc.salonName, datetime.strptime(req['time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M %A %d-%m-%Y'), cancel_mes)
                    
                    if len(message) <= 160:
                        
                        queueMSM(salonAcc, message, appointment.customer.mobile)
                    else:
                        message = '{}: Your appointment at {} has been successfully booked.'.format(salonAcc.salonName, datetime.strptime(req['time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M %A %d-%m-%Y'))
                        queueMSM(salonAcc, message, appointment.customer.mobile)
                        cancel_mes = '{}: To cancel please follow the link. https://{}/appointment-cancel/?id={}'.format(salonAcc.salonName, salonAcc.website, appointment.cancelID)
                        queueMSM(salonAcc, cancel_mes, appointment.customer.mobile)
                    
                    rev = reverse('appointment_succeed')
                    rev = '{}?id={}&time={}'.format(rev, req['appoinmentID'], req['time'])
                    # temp_appointment.delete()
                    return HttpResponseRedirect(rev)  
                else:

                    rev = reverse('appointment_confirm')
                    rev = '{}?id={}'.format(rev, temp_appointment.appoinmentID)
                    return HttpResponseRedirect(rev)



        else:
            rev = reverse('verify')
            rev = '{}?id={}'.format(rev, req['appoinmentID'])
            return HttpResponseRedirect(rev)
    else:
        extraservices = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)
        # print(extraservices)
        serviceblocks = ServiceBlock.objects.filter(salonAcc=salonAcc)

        cleanupapps = TemplateAppointment.objects.filter(createdTime__lt=timezone.now() - timedelta(minutes=100), waitFrom__isnull=True, salonAcc=salonAcc)
        cleanupapps.delete()
        appoinmentID = request.GET.get('id')
        if request.GET.get('rem') == '1':
            max_age = 3600*24*60
        else:
            max_age = 1800

            

        if request.GET.get('date'):
            appID = request.GET.get('id')
            appointment = get_object_or_404(TemplateAppointment, appoinmentID=appID, salonAcc=salonAcc)
            appnt = Appointment(salonAcc=appointment.salonAcc,
                                notice=appointment.notice,
                                service=appointment.appoinmentService,
                                )
    
            extras = []
            for extra in appointment.appoinmentEXtra.all():
                extras.append(extra)

            temp_appnt = TemplateAppointment(appnt, extras)
            temp_appnt.appointment.dateTime = datetime.strptime(request.GET.get('date'), "%Y-%m-%d")
            availTimes = temp_appnt.get_available_times()
            context = {
                'availTimes':availTimes,
                'salonAcc':salonAcc
            }
            # logger.debug('customer views  appointment confirm get avail times {}'.format(availTimes))
            return render(request, 'customers/availTimes_ajax.html', context)
        appointment = TemplateAppointment.objects.filter(appoinmentID=appoinmentID, salonAcc=salonAcc).first()
        if not appointment:
            return render(request, 'customers/appointment_timeout.html')


        if appointment.waitTo:
            context = {
                'appointment':appointment,
                'salonAcc':salonAcc
                }
            return render(request, 'customers/waitting_list_succeed.html', context)    
        if appointment.verified:
            appnt = Appointment(salonAcc=appointment.salonAcc,
                                notice=appointment.notice,
                                service=appointment.appoinmentService,
                                )
    
            extras = []
            for extra in appointment.appoinmentEXtra.all():
                extras.append(extra)

            # temp_appnt = TemplateAppointments(appnt, extras)
            # availDates = temp_appnt.get_available_dates()

            waitting_list_dates = []
            # _date = timezone.now()
            for i in range(0, 6):
                _date = timezone.now() + timedelta(days=i)
                def openingTime(_date, salonAcc):
                    if SpecialOpenTime.objects.filter(salonAcc=salonAcc, date=_date):
                        return SpecialOpenTime.objects.filter(salonAcc=salonAcc, date=_date).first()
                    if not ClosedDay.objects.filter(salonAcc=salonAcc, date=_date):
                        return OpenTimes.objects.filter(day=_date.weekday(), salonAcc=salonAcc).first()
                    else:
                        logger.debug('Close day')
                        return OpenTimes.objects.filter(day=_date.weekday(), salonAcc=salonAcc).first()
                openingTime = openingTime(_date, salonAcc)
                if openingTime.openTime and openingTime.closeTime:      

                    waitting_list_dates.append(_date)

            context = {
    
                'extraservices':extraservices.all(),
                'serviceblocks':serviceblocks,
                'salonAcc':salonAcc,
                'appoinmentID':appoinmentID,
                # 'availDates':availDates,
                # 'availTimes':availTimes,
                # 'appointment':appointment,
                'waitting_list_dates':waitting_list_dates,
        
            }


                
            letters = string.ascii_letters
            session = ''.join(random.choice(letters) for i in range(32))
            # customer, created = Customer.objects.get_or_create(mobile=appointment.appoinmentMobile, defaults={'salonAcc':salonAcc,
            #                                             'firstName':appointment.appoinmentFName,
            #                                             'lastName':appointment.appoinmentLName}
            #                                             )
            customer = Customer.objects.filter(mobile=appointment.appoinmentMobile, salonAcc=salonAcc,
                                                        firstName=appointment.appoinmentFName,
                                                        lastName=appointment.appoinmentLName
                                                        ).first()
            if customer == None:
                customer = Customer.objects.create(mobile=appointment.appoinmentMobile, salonAcc=salonAcc,
                                            firstName=appointment.appoinmentFName,
                                            lastName=appointment.appoinmentLName
                                            )
            Session, created = CustomerSession.objects.update_or_create(customer=customer, defaults={'session':session, 'expired':(timezone.now() + timedelta(seconds=max_age))})
            context['customer'] = customer
            response = render(request, 'customers/appointment_confirm.html', context)
            response.set_cookie(key='cus_session', value=session, max_age=max_age)
            return response
        else:
            rev = reverse('verify')
            rev = '{}?id={}'.format(rev, appoinmentID)
            return HttpResponseRedirect(rev)  
    # except Exception as e:
    #     logger.exception(e, exc_info=True)

def waitting_list_succeed(request):
    salonAcc = get_object_or_404(SalonAccount, website=request.META['HTTP_HOST'])
    req = request.GET
    appID = req.get('id')
    appointment = TemplateAppointment.objects.filter(salonAcc=salonAcc, appoinmentID=appID).first()
    if not appointment:
        return render(request, 'customers/appoitment_timeout.html')

    context = {
        'appointment':appointment,
        'salonAcc':salonAcc
        }
    return render(request, 'customers/waitting_list_succeed.html', context)

def appointment_succeed(request):
    salonAcc = get_object_or_404(SalonAccount, website=request.META['HTTP_HOST'])
    req = request.GET
    if req.get('cancelled'):
        cancelled = True
        context = {
            'cancelled':cancelled,
            'salonAcc':salonAcc
        }
    if req.get('id'):
        appID = req.get('id')
        appointment = get_object_or_404(TemplateAppointment, salonAcc=salonAcc, appoinmentID=appID)
        try:
            apptime = datetime.strptime(req.get('time'), '%Y-%m-%d %H:%M:%S')
        except:
            return HttpResponseNotFound

        context = {
            'appointment':appointment,
            'apptime':apptime,
            'salonAcc':salonAcc
            }
        appointment.delete()
    return render(request, 'customers/appointment_succeed.html', context)

def update_appointment(request):
    reqst = request
    salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
    cancelID = reqst.GET.get('id')
    appointment = get_object_or_404(Appointment, salonAcc=salonAcc, cancelID=cancelID)
    
    if appointment.dateTime - datetime.now() < timedelta(hours=1):
        serviceblocks = ServiceBlock.objects.filter(salonAcc=salonAcc)
        extraservices = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)


    context = {
        'appointment':appointment,  

        'serviceblocks':serviceblocks,
        'extraservices':extraservices,


        'salonAcc':salonAcc,


        
    }

    if request.method == 'POST':
        req = request.POST
        # salonAcc = request.user.salonAcc
        if 'update_status' in req:
            if req['appointment_status']:

                # appointment = Appointment.objects.get(pk=pk, salonAcc=salonAcc)
                appointment.status = AppointmentStatus.objects.get(pk=req['appointment_status'], salonAcc=salonAcc)
                appointment.save()
        # rev = reverse('appointments')
        # rev = '{}?viewdate={}'.format(rev, appDate)        
        # return HttpResponseRedirect(rev)
            messages.success(request, 'Appointments status updated')
            return render(request, 'customers/appointment_update_form.html', context)
        if 'delete' in req:
            for key in req:
                if key.isdigit():
                    appnts = Appointment.objects.get(pk=key, salonAcc=salonAcc)
                    appnts.delete()
            appnts = Appointment.objects.filter(customer=appointment.customer, salonAcc=salonAcc).exclude(pk=pk)
            active_apps = False
            for actappnt in appnts:
                if actappnt != appointment:
                    if not actappnt.status:
                        active_apps = True
                        break

            context['appnts'] = appnts
            context['active_apps'] = active_apps
            context['salonAcc'] = salonAcc
            datetime.s

            messages.success(request, 'Appointments deleted')
            return render(request, 'customers/appointment_update_form.html', context)
        if 'confirm' in req:
            current_app = get_object_or_404(Appointment, pk=req['current_appointment'])
            waiting_apps = TemplateAppointment.objects.filter(salonAcc=salonAcc, waitFrom__lte=current_app.dateTime, waitTo__gte=current_app.dateTime)
            print(waiting_apps)
            cancel_time = current_app.dateTime.strftime('%H:%M:%S %A %d-%m-%Y')
            for _appnt in waiting_apps:
                _appnt.send_notify(f'{salonAcc.salonName}: We have cancelation at {cancel_time}. Please go to https://{salonAcc.website} to book your appointment. Thank you')
            current_app.delete()
            return HttpResponseRedirect(reverse('appointments'))
        if 'update_appointment' in req:
            apnt_time = 0
            service = ServiceBlock.objects.filter(pk=req["service"], salonAcc=salonAcc).first()
            

            custm = appointment.customer
            

            appntDateTime = datetime.strptime(req['time'], "%Y-%m-%d %H:%M:%S")
            temp_appnt = TempAppointment(customer=custm,
                                        salonAcc=salonAcc,
                                        dateTime=appntDateTime,
                                        notice=req['notice'],
                                        service=service,
                                        )
            temp_appnt.temp_extras = []
            for extra in extraservices:
                if extra.name in req:
                    temp_appnt.temp_extras.append(extra)
            if req['stylist']:
                temp_appnt.stylist = SalonStylist.objects.filter(salonAcc=salonAcc, pk=req['stylist']).first()
            appointment = temp_appnt.save_appointment(current_appointment=appointment)
            if appointment:
                    # appointment = resp['message']
                extraservicestr = ''
                for extra in appointment.extras.all():
                    extraservicestr += (extra.name + ' ')
            if 'send_sms' in req:
                if appointment.customer.mobile:
                    cancel_mes = 'To cancel go to. https://{}/appointment-cancel/?id={}'.format(salonAcc.website, appointment.cancelID)
                    message = '{}: Your appointment at {} has been successfully booked. {}'.format(salonAcc.salonName, datetime.strptime(req['time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M %A %d-%m-%Y'), cancel_mes)
                    
                    if len(message) <= 160:
                        
                        queueMSM(salonAcc, message, appointment.customer.mobile)
                    else:
                        message = '{}: Your appointment at {} has been successfully booked.'.format(salonAcc.salonName, datetime.strptime(req['time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M %A %d-%m-%Y'))
                        queueMSM(salonAcc, message, appointment.customer.mobile)
                        cancel_mes = '{}: To cancel please follow the link. https://{}/appointment-cancel/?id={}'.format(salonAcc.salonName, salonAcc.website, appointment.cancelID)
                        queueMSM(salonAcc, cancel_mes, appointment.customer.mobile)
    
            rev = reverse('appointments')
            rev = '{}appointment/update/{}'.format(rev, appointment.pk)
            return HttpResponseRedirect(rev)


            

    else:

        return render(request, 'customers/appointment_update_form.html', context)

def appointment_cancel(request):
        
    req = request.GET
    salonAcc = get_object_or_404(SalonAccount, website=request.META['HTTP_HOST'])
    cancelID = req.get('id')

    appointment = get_object_or_404(Appointment, salonAcc=salonAcc, cancelID=cancelID)
    context = {
    'appointment':appointment,
    'salonAcc':salonAcc
    }
    print(appointment)
    if appointment.dateTime - datetime.now() > timedelta(hours=1):

    # try:
    #     apptime = datetime.strptime(req.get('time'), '%Y-%m-%d %H:%M:%S')
    # except:
    #     return HttpResponseNotFound

        if request.method == 'POST':
            appointment = get_object_or_404(Appointment, salonAcc=salonAcc, cancelID=request.POST['appointment'])

            waiting_apps = TemplateAppointment.objects.filter(salonAcc=salonAcc, waitFrom__lte=appointment.dateTime, waitTo__gte=appointment.dateTime)
            cancel_time = appointment.dateTime.strftime('%H:%M:%S %A %d-%m-%Y')
            for _appnt in waiting_apps:
                print('Temp appointment ID', _appnt.appoinmentID)
                _appnt.send_notify(f'{salonAcc.salonName}: We have cancelation at {cancel_time}. Please go to https://{salonAcc.website}/appointment-confirm/?id={_appnt.appoinmentID:} to book your appointment. Thank you')
            

            appointment.delete()
            rev = reverse('appointment_succeed')
            rev = '{}?cancelled=1'.format(rev)
            # temp_appointment.delete()
            return HttpResponseRedirect(rev)  

        return render(request, 'customers/appointment_cancel.html', context)
    else:
        return render(request, 'customers/appointment_cancel_timeout.html', context)

@salon_account_check    
@manager_required
def stylistTimeOff(request):
    if request.method =="POST":
        req = request.POST
    else:
        pass

@login_required
@salon_account_check
@manager_required
@permission_required('add_storelocker')
def add_locker(request):
    if request.method == 'POST':
        user = request.user
        lastLockers = StoreLocker.objects.filter(salonAcc=user.salonAcc).order_by('-boxNumber').first()
        if lastLockers:
            lastLockers.boxNumber
    else:
        return HttpResponse('ok')

from django.views.decorators.csrf import csrf_exempt

@login_required
@salon_account_check
# @manager_required
def customer_create(request):
    reqst = request
    salonAcc = reqst.user.salonAcc
    lockers = StoreLocker.objects.filter(customer__isnull=True, salonAcc=salonAcc).order_by('boxNumber')
    if not lockers:
        lastLockers = StoreLocker.objects.filter(salonAcc=salonAcc).order_by('-boxNumber').first()
        if not lastLockers:
            StoreLocker.objects.create(salonAcc=salonAcc, boxNumber=1)
        else:
            StoreLocker.objects.create(salonAcc=salonAcc, boxNumber=(lastLockers.boxNumber + 1))
            lockers = StoreLocker.objects.filter(salonAcc=salonAcc, boxNumber=(lastLockers.boxNumber + 1))

    context = {
        'lockers':lockers,
        'salonAcc':salonAcc
    }
    if request.method == 'POST':
        request = request
        user = request.user
        req = request.POST


        customer = Customer.objects.filter(salonAcc=salonAcc, firstName=req['firstName'], lastName=req['lastName'], mobile=req['mobile'],).first()

        if not customer:

            cus = Customer(firstName=req['firstName'],
                            lastName=req['lastName'],
                            mobile=req['mobile'],
                            tel=req['tel'],
                            address_1=req['address_1'],
                            address_2=req['address_2'],
                            town=req['town'],
                            postCode=req['postCode'],                    
                            salonAcc=user.salonAcc)
            cus.save()


            if 'locker' in req:
                try:
                    StoreLocker.objects.filter(salonAcc=salonAcc, boxNumber=req['locker']).update(customer=cus)
                except:
                    StoreLocker.objects.create(salonAcc=salonAcc, boxNumber=req['locker'], customer=cus)
            # rev = reverse('update-customer', kwargs={'pk': cus.pk})
            rev = reverse('customers')
            return HttpResponseRedirect(rev)  
        else:
            messages.error(request, 'Can not create customer! {} {} already exit'.format(req['firstName'], req['lastName']))
            return render(request, 'customers/customer_create_form.html', context)


    else:
        return render(request, 'customers/customer_create_form.html', context)

@login_required
@salon_account_check
def boxes(request):
    cleanDate = request.GET.get('viewdate')

    if request.method == 'POST':
        req = request.POST

        if 'change_date' in req:
            if 'viewdate' in req:

                viewdatestr = req['viewdate']
                viewdate = datetime.strptime(viewdatestr, '%Y-%m-%d').date().strftime("%b %d %Y")
                valueDate = datetime.strptime(viewdatestr, '%Y-%m-%d').date().strftime("%Y-%m-%d")
                # print(str(viewdate))
                # print(type(viewdate))

            else:
                dnow = date.today()
                viewdate = dnow.strftime("%b %d %Y")
                valueDate = dnow.strftime("%Y-%m-%d")

            optimestr = str(viewdate) + ' ' + str(time(9, 0, 0))
            cltimestr = str(viewdate) + ' ' + str(time(17, 30, 0))
            optime = datetime.strptime(optimestr, '%b %d %Y %H:%M:%S')
            cltime = datetime.strptime(cltimestr, '%b %d %Y %H:%M:%S')


            appnts = Appointment.objects.filter(dateTime__range=(optime, cltime))
            lockers = []
            for appnt in appnts:
                locker = StoreLocker.objects.filter(customer=appnt.customer).first()
                lockers.append(locker)
            # print(lockers)

            context = {
                'lockers': lockers,
                'viewdate': viewdate,
                'valueDate': valueDate,
                'salonAcc':salonAcc

            }
            
            # print(appointments)
            return render(request, 'customers/boxes.html', context)
        elif 'clean' in req:
            for key, value in req.items():
                try:
                    # print(req['cleanDate'])
                    locker = StoreLocker.objects.filter(boxNumber=int(key)).first()
                    locker.clean = datetime.strptime(req['cleanDate']+ ' ' + '18:00:00', '%Y-%m-%d %H:%M:%S')
                    locker.save()
                except:
                    pass
            return render(request, 'customers/boxes_cleaned.html')

    else:
        dnow = date.today()
        viewdate = dnow.strftime("%b %d %Y")
        valueDate = dnow.strftime("%Y-%m-%d")
        optimestr = str(viewdate) + ' ' + str(time(9, 0, 0))
        cltimestr = str(viewdate) + ' ' + str(time(17, 30, 0))
        optime = datetime.strptime(optimestr, '%b %d %Y %H:%M:%S')
        cltime = datetime.strptime(cltimestr, '%b %d %Y %H:%M:%S')


        appnts = Appointment.objects.filter(dateTime__range=(optime, cltime))
        lockers = []
        for appnt in appnts:
            locker = StoreLocker.objects.filter(customer=appnt.customer).first()
            lockers.append(locker)

        context = {
            'lockers': lockers,
            'viewdate': viewdate,
            'valueDate': valueDate,
            'salonAcc':salonAcc

        }
        return render(request, 'customers/boxes.html', context)
@login_required
@salon_account_check
def box_check(request, pk):
    locker = StoreLocker.objects.get(pk=pk)
    locker.clean = timezone.now()
    locker.save()
    return render(request, 'customers/box_cleaned.html')

@login_required
@salon_account_check
def clean_boxs(request):
    if request.method == 'POST':
        req = request.POST
        if 'boxes' in req:

            boxes = req['boxes'].split(',')
            for box in boxes:
                locker = StoreLocker.objects.get(pk=box)
                print(locker)
                locker.clean = timezone.now()
                locker.save()
    
        return render(request, 'customers/box_cleaned.html')

    return render(request, 'customers/clean_boxs.html')

@login_required
@salon_account_check
def customers(request):
    try:
        reqst = request
        salonAcc = reqst.user.salonAcc
        # # lockers = StoreLocker.objects.all()
        

        # if request.method == 'POST':
        #     appointments = Appointment.objects.filter(salonAcc=salonAcc)
        #     lockers = StoreLocker.objects.filter(salonAcc=salonAcc)
        #     req = request.POST
        #     firstNameq = Customer.objects.filter(salonAcc=salonAcc, firstName__icontains=req['search'])
        #     lastNameq = Customer.objects.filter(salonAcc=salonAcc, lastName__icontains=req['search'])
        #     customers = firstNameq | lastNameq
        #     for customer in customers:
        #         for locker in lockers:
        #             # print(locker.boxNumber)
        #             if locker.customer == customer:
        #                 # print(locker.boxNumber)
        #                 customer.locker = locker.boxNumber
        #                 customer.lastChecked = locker.clean
        #                 # print(customer.locker)
        #         for appointment in appointments:
        #             if appointment.customer == customer:
        #                 # print(appointment.dateTime)
        #                 customer.appointmt = appointment.dateTime
                        




        #     context = {
        #         'customers': customers,
        #         'salonAcc':salonAcc
        


        #     }

        #     return render(request, 'customers/customers.html', context)
        # else:
        #     customers = Customer.objects.filter(salonAcc=salonAcc)
        #     lockers = StoreLocker.objects.filter(salonAcc=salonAcc)
        #     for customer in customers:
        #         for locker in lockers:
        #             # print(locker.boxNumber)
        #             if locker.customer == customer:
        #                 # print(locker.boxNumber)
        #                 customer.locker = locker.boxNumber
        #                 customer.lastChecked = locker.clean

        context = {
            # 'customers' : customers,
            'salonAcc':salonAcc
        }
        return render(request, 'customers/customers.html', context)
    except Exception as e:
        logger.exception(e, exc_info=True)

@login_required
@salon_account_check
def get_customer(request):
    reqst = request
    salonAcc = reqst.user.salonAcc
    
    callerIDs = reqst.GET.get('callerID')
    if callerIDs:
        for ID in callerIDs:
            customer = Customer.objects.filter(mobile=callerID, salonAcc=salonAcc).first()
            not_turned_up = NotTurnedUp.objects.filter(customer=customer)

        print('not turned up', not_turned_up)
    else:
        customer = None
        not_turned_up = None
    context = {
        'customer':customer,
        'callerID':callerID,
        'salonAcc':salonAcc,
        'not_turned_up':not_turned_up

    }
    return render(request, 'customers/customer_info.html', context)

@login_required
@salon_account_check
def get_customer_api(request):
    reqst = request
    salonAcc = reqst.user.salonAcc
    
    callerID = reqst.GET.get('callerID')
    if callerID:

        customer = Customer.objects.filter(mobile=callerID, salonAcc=salonAcc).first()
        from django.forms.models import model_to_dict    
        return JsonResponse(model_to_dict(customer))

    else:
        return HttpResponse('')
 

@login_required
@salon_account_check
def customer_search(request):
    from django.db.models import Q
    reqst = request
    salonAcc = reqst.user.salonAcc
    customers = None
    
    if reqst.GET.get('firstname') != None:

        if Customer.objects.filter(firstName__icontains=reqst.GET.get('firstname'), salonAcc=salonAcc).exists():
            customers = Customer.objects.filter(firstName__icontains=reqst.GET.get('firstname'), salonAcc=salonAcc)
    elif reqst.GET.get('lastname') != None:

        if Customer.objects.filter(lastName__icontains=reqst.GET.get('lastname'), salonAcc=salonAcc).exists():
            customers = Customer.objects.filter(lastName__icontains=reqst.GET.get('lastname'), salonAcc=salonAcc)
    elif (reqst.GET.get('firstname') != None) and (reqst.GET.get('lastname') != None):
       
        if Customer.objects.filter(lastName__icontains=reqst.GET.get('lastname'), firstName__icontains=reqst.GET.get('firstname'), salonAcc=salonAcc).exists():
            customers = Customer.objects.filter(lastName__icontains=reqst.GET.get('lastname'), firstName__icontains=reqst.GET.get('firstname'), salonAcc=salonAcc)
    elif reqst.GET.get('box') != None:

        for locker in StoreLocker.objects.filter(boxNumber=reqst.GET.get('box'), salonAcc=salonAcc):
            if locker.customer:
                customers = Customer.objects.filter(pk=locker.customer.pk)
    elif reqst.GET.get('mobile') != None:
        print(reqst.GET.get('mobile'))
        if Customer.objects.filter(mobile__icontains=reqst.GET.get('mobile'), salonAcc=salonAcc).exists():
            customers = Customer.objects.filter(mobile__icontains=reqst.GET.get('mobile'), salonAcc=salonAcc)
            print('Customer: ', customers)
    if customers:
        customers.order_by('firstName')


    
    # customers = customers_first

        for customer in customers:
            try:
                customer.box = StoreLocker.objects.get(customer=customer)
                customer.not_turned_up = NotTurnedUp.objects.filter(customer=customer)
            except:
                pass
    context = {
            'customers':customers[:50],
            'salonAcc':salonAcc
        }    
    return render(request, 'customers/customer_search.html', context)

@login_required
@salon_account_check
def customer_delete(request, pk):
    reqst = reques
    salonAcc = reqst.user.salonAcc
    if reqst.method == 'GET':
        customer = Customer.objects.get(pk=pk, salonAcc=salonAcc)
        Customer.objects.get(pk=pk, salonAcc=salonAcc).delete()
        context = {
            'customer':customer,
            'salonAcc':salonAcc
        }
    return render(request, 'customers/customer_deleted.html', context)

@login_required
@salon_account_check
def customer_update(request, pk):
    reqst = request
    salonAcc = reqst.user.salonAcc

    if request.method == 'POST':
        customer = Customer.objects.get(pk=pk, salonAcc=salonAcc)
        req = request.POST
        if 'firstName' in req:
            
            customer.firstName = req['firstName']
            customer.save()
        if 'lastName' in req:

            customer.lastName = req['lastName']
            customer.save()
        if 'mobile' in req:

            customer.mobile = req['mobile']
            customer.save()
        if 'notice' in req:

            customer.notice = req['notice']
            customer.save()
        if 'locker' in req:
            try:
                locker = StoreLocker.objects.filter(boxNumber=req['locker'], salonAcc=salonAcc).first()
                locker.customer = customer
                locker.save()
            except:
                pass
                    




        context = {
                'salonAcc':salonAcc


        }

        return render(request, 'customers/customers.html', context)
    else:
        customer = get_object_or_404(Customer, pk=pk, salonAcc=salonAcc)
        locker = StoreLocker.objects.filter(customer=customer, salonAcc=salonAcc).first()
        lockers = StoreLocker.objects.filter(customer__isnull=True, salonAcc=salonAcc)
        customers = Customer.objects.filter(salonAcc=salonAcc)
        cus_appointments = Appointment.objects.filter(customer=customer, salonAcc=salonAcc)
        not_turned_up = NotTurnedUp.objects.filter(salonAcc=salonAcc, customer=customer)
        context = {
            'customers': customers,
            'customer': customer,
            'locker':locker,
            'lockers':lockers,
            'salonAcc':salonAcc,
            'cus_appointments':cus_appointments,
            'not_turned_up':not_turned_up


        }
        return render(request, 'customers/customer_update.html', context)


from customers.models import OpenTimes
from django.core.cache import cache
@login_required
@salon_account_check
def appointments(request):

    reqst = request
    salonAcc = reqst.user.salonAcc
    if reqst.method == 'POST':
        req = reqst.POST
        if 'waiting_submit' in req:
            print('waiting_submit')
            letters = string.ascii_letters
            appoinmentID = ''.join(random.choice(letters) for i in range(25))
            letters = string.digits
            appoinmentOTP = ''.join(random.choice(letters) for i in range(4))
            templateAppoint = TemplateAppointment(appoinmentID=appoinmentID,
                                                    appoinmentFName=req['firstname'],
                                                    appoinmentLName=req['lastname'],
                                                    appoinmentMobile=req['mobile'],
                                                    appoinmentService=ServiceBlock.objects.filter(salonAcc=salonAcc, pk=req['service']).first(),
                                                    appoinmentOTP=appoinmentOTP,
                                                    salonAcc=salonAcc,
                                                    )

            templateAppoint.save()
            extras = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)
            for extra in extras:
                if extra.name in req:
                    # print(templateAppoint)
                    # print(extra)
                    templateAppoint.appoinmentEXtra.add(extra)
                    templateAppoint.save()

            templateAppoint.waitFrom = datetime.strptime('{} {}'.format(req['wait_date'], req['waitting_time_from']), '%Y-%m-%d %H:%M:%S')
            templateAppoint.waitTo = datetime.strptime('{} {}'.format(req['wait_date'], req['waitting_time_to']), '%Y-%m-%d %H:%M:%S')
            templateAppoint.save()
            rev = reverse('appointments')

            return HttpResponseRedirect(rev)
#             appoinmentID: 
# firstname: Quang
# lastname: Dam
# mobile: 07401384305
# service: 16
# wait_date: 2021-05-29
# waitting_time_from: 09:00:00
# waitting_time_to: 18:00:00
# waiting_submit: 
        else:
            return HttpResponseNotFound()
    else:
        
        if not salonAcc:
            return HttpResponseRedirect(reverse('salon-account'))
        closed = False
        stylists = SalonStylist.objects.filter(salonAcc=salonAcc)
        if reqst.method == 'GET':
            if not reqst.GET.get('viewdate'):
                viewdate = datetime.today()
            elif reqst.GET.get('viewdate'):
                viewdate = datetime.strptime(reqst.GET.get('viewdate'), '%Y-%m-%d')
            if SpecialOpenTime.objects.filter(date=viewdate, salonAcc=salonAcc):
                # print('specila openday')
                closed = False
                opening_time = SpecialOpenTime.objects.filter(date=viewdate, salonAcc=salonAcc).first()
            elif not ClosedDay.objects.filter(date=viewdate, salonAcc=salonAcc).first():
                # print(' not close day')
                opening_time = OpenTimes.objects.filter(salonAcc=salonAcc, day=viewdate.weekday()).first()
                closed = not (opening_time.openTime and opening_time.closeTime)

            else:
                closed = True
        # print(closed)
        if not closed:
            try:
                response = cache.get(f'viewdate_{viewdate.strftime("%Y-%m-%d")}')
                if response:
                    return response
                else:
                    raise
            except:
                pass
            rows = []
            openTime = datetime.strptime('{} {}'.format(viewdate.strftime('%Y-%m-%d'), opening_time.openTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
            closeTime = datetime.strptime('{} {}'.format(viewdate.strftime('%Y-%m-%d'), opening_time.closeTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
            slotTime = openTime
            waiting_list = TemplateAppointment.objects.filter(waitFrom__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0), waitFrom__lte=timezone.now().replace(hour=23, minute=59, second=59, microsecond=999), waitTo__gte=timezone.now())
            while slotTime <= closeTime:
                    timeblock = []
                    timeblock.append(slotTime.strftime('%H:%M:%S'))
                    for stylist in stylists:
                        timeblock.append('Available')
                    appnts = Appointment.objects.filter(salonAcc=salonAcc, dateTime__range=(openTime, closeTime))
                    # logger.debug(f'appointments query set {appnts}')
                    for a, appnt in enumerate(appnts, start=1):
                        appnt.length = appnt.service.length
                        for extra in appnt.extras.all():
                            appnt.length += extra.length

                        r = (a*60)%180                    
                        b = (a*60)%180
                        g = (a*60)%180
                        for i, stylist in enumerate(stylists, start=1):
                            # logger.debug(f' app stylist {appnt.stylist}  checking stylist {stylist}')
                            if appnt.stylist == stylist:
                                # print('app datetime is naive :',appnt.dateTime.is_naive())
                                if (appnt.dateTime <= slotTime) and ((appnt.dateTime+ timedelta(minutes=appnt.length-1)) > slotTime ):
                                    if appnt.service.pedicure_chair_length:
                                        b = 0
                                    for extra in appnt.extras.all():
                                        if extra.length < 0:
                                            r = 255
                                    appnt.r = r
                                    appnt.b = b
                                    appnt.g = g
                                    appnt.locker = StoreLocker.objects.filter(salonAcc=salonAcc, customer=appnt.customer).first()
                                    timeblock[i] = appnt
                    rows.append(timeblock)
                    slotTime += timedelta(minutes=15)
            waitting_list_dates = []
            # _date = timezone.now()
            for i in range(0, 7):
                _date = timezone.now() + timedelta(days=i)
                def openingTime(_date, salonAcc):
                    if SpecialOpenTime.objects.filter(salonAcc=salonAcc, date=_date):
                        return SpecialOpenTime.objects.filter(salonAcc=salonAcc, date=_date).first()
                    if not ClosedDay.objects.filter(salonAcc=salonAcc, date=_date):
                        return OpenTimes.objects.filter(day=_date.weekday(), salonAcc=salonAcc).first()
                    else:
                        logger.debug('Close day')
                        return OpenTimes.objects.filter(day=_date.weekday(), salonAcc=salonAcc).first()
                openingTime = openingTime(_date, salonAcc)
                if openingTime.openTime and openingTime.closeTime:      

                    waitting_list_dates.append(_date)
            extraservices = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)
            serviceblocks = ServiceBlock.objects.filter(salonAcc=salonAcc)

            context = {

                'rows': rows,
                # 'weekday': weekday,
                'stylists': stylists,
                'viewdate':viewdate,
                'closed':closed,
                'salonAcc':salonAcc,
                'waiting_list':waiting_list,
                'waitting_list_dates':waitting_list_dates,
                'extraservices':extraservices.all(),
                'serviceblocks':serviceblocks,

            }
            response = render(request, 'customers/appointments.html', context)
            cache.set(f'viewdate_{viewdate.strftime("%Y-%m-%d")}', response)
            return response
        else:
            context = {
                'viewdate':viewdate,
                'closed':closed,
                'salonAcc':salonAcc

            }
            return render(request, 'customers/appointments.html', {'closed':closed})

@login_required
@salon_account_check
# @manager_required
def appointment_create(request):
    reqst = request
    salonAcc = reqst.user.salonAcc
    stylists = SalonStylist.objects.filter(salonAcc=salonAcc)
    extraservices = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)
    serviceblocks = ServiceBlock.objects.filter(salonAcc=salonAcc)
    appntDate = request.GET.get('viewdate')
    appntTime = request.GET.get('time')
    strdt = appntDate + ' ' + appntTime
    appntTimeob = datetime.strptime(str(strdt), "%Y-%m-%d %H:%M:%S")
            
    context = {
        'stylists':stylists,
        'prefer_time':appntTimeob,
        'serviceblocks':serviceblocks,
        'extraservices':extraservices,
        'salonAcc':salonAcc

    }

    if request.method == 'POST':
        apnt_time = 0
        req = request.POST
        service = ServiceBlock.objects.filter(pk=req["service"], salonAcc=salonAcc).first()
        if req['cus_id']:
            cus = Customer.objects.filter(salonAcc=salonAcc,firstName=req['firstName'], lastName=req['lastName'], pk=req['cus_id']).first()
            if not cus:

                custm = Customer(salonAcc=salonAcc,
                        firstName=req['firstName'],
                        lastName=req['lastName'],
                        mobile=req['mobile'],
                        )
                custm.save()
            
                
            else:
                custm = Customer.objects.filter(salonAcc=salonAcc, firstName=req['firstName'], lastName=req['lastName'], pk=req['cus_id']).first()
        else:
            custm = Customer(salonAcc=salonAcc,
                    firstName=req['firstName'],
                    lastName=req['lastName'],
                    mobile=req['mobile'],
                    )
            custm.save()

        appntDateTime = datetime.strptime(req['time'], "%Y-%m-%d %H:%M:%S")
        temp_appnt = TempAppointment(customer=custm,
                                    salonAcc=salonAcc,
                                    dateTime=appntDateTime,
                                    notice=req['notice'],
                                    service=service,
                                    )
        temp_appnt.temp_extras = []
        for extra in extraservices:
            if extra.name in req:
                temp_appnt.temp_extras.append(extra)
        if req['stylist']:
            temp_appnt.stylist = SalonStylist.objects.filter(salonAcc=salonAcc, pk=req['stylist']).first()
        
        appointment = temp_appnt.save_appointment()

 
        # setcahce = threading.Thread(target = cacheAvailables.setAvailableCache, name = 'thread{}'.format('setAvailableCache thread'), args=())
        # setcahce.daemon = True
        # setcahce.start()
  
        # print(AvailableTimesCache(salonAcc=salonAcc, stylist=appointment.stylist, date=appointment.dateTime.date()).getAvailableCache())
        if appointment:
            cacheAvailables = AvailableTimesCache(salonAcc=salonAcc, stylist=appointment.stylist, date=appointment.dateTime.date())
            cacheAvailables.deleteAvailableCache()
            print(cacheAvailables.setAvailableCache())
                    # appointment = resp['message']

            if appointment.customer.mobile:
                cancel_mes = 'To cancel go to. https://{}/appointment-cancel/?id={}'.format(salonAcc.website, appointment.cancelID)
                message = '{}: Your appointment at {} has been successfully booked. {}'.format(salonAcc.salonName, datetime.strptime(req['time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M %A %d-%m-%Y'), cancel_mes)
                
                if len(message) <= 160:
                    
                    queueMSM(salonAcc, message, appointment.customer.mobile)
                else:
                    message = '{}: Your appointment at {} has been successfully booked.'.format(salonAcc.salonName, datetime.strptime(req['time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M %A %d-%m-%Y'))
                    queueMSM(salonAcc, message, appointment.customer.mobile)
                    cancel_mes = '{}: To cancel please follow the link. https://{}/appointment-cancel/?id={}'.format(salonAcc.salonName, salonAcc.website, appointment.cancelID)
                    queueMSM(salonAcc, cancel_mes, appointment.customer.mobile)
  
        # rev = reverse('update-appointment', kwargs={'pk': appointment.pk})
        # rev = '{}appoitment/update/{}'.format(rev, appointment.pk)
            rev = reverse('appointments')
            rev = rev + '?viewdate={}'.format(appointment.dateTime.strftime('%Y-%m-%d'))
        
            return HttpResponseRedirect(rev)
        else:
            messages.error(request, 'Appointment unsuccessful booked')
            return render(request, 'customers/appointment_create_form.html', context)

    else:
        return render(request, 'customers/appointment_create_form.html', context)


@login_required
@salon_account_check
def appointments_view(request):
    reqst = request
    salonAcc = reqst.user.salonAcc
    custm = request.GET.get('custm')
    cus = get_object_or_404(Customer, pk=int(custm), salonAcc=salonAcc)
    appnts = Appointment.objects.filter(customer=cus, salonAcc=salonAcc).order_by('dateTime')
    context = {
        'cus':cus,
        'appnts':appnts,
        'salonAcc':salonAcc
    }

    if request.method == 'POST':
        req = request.POST
        for key in req:
            if key.isdigit():
                appnts = Appointment.objects.get(pk=key, salonAcc=salonAcc)
                appnts.delete()
        appnts = Appointment.objects.filter(customer=cus, salonAcc=salonAcc)
        context = {
            'cus':cus,
            'appnts':appnts,
            'salonAcc':salonAcc
        }
        return render(request, 'customers/appointments_view.html', context)
    else:
    # print(appntDate)
        return render(request, 'customers/appointments_view.html', context)

@login_required
@salon_account_check
def appoinment_update(request, pk):
    reqst = request
    salonAcc = reqst.user.salonAcc
    stylists = SalonStylist.objects.filter(salonAcc=salonAcc)
    serviceblocks = ServiceBlock.objects.filter(salonAcc=salonAcc)
    extraservices = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)
    appointment = get_object_or_404(Appointment, pk=pk, salonAcc=salonAcc)
    locker = StoreLocker.objects.filter(salonAcc=salonAcc, customer=appointment.customer).first()
    # print(appointment.dateTime)
    appnts = Appointment.objects.filter(customer=appointment.customer).exclude(pk=pk)
    extras = []
    for extra in appointment.extras.all():
        extras.append(extra)

    # appnt = TemplateAppointments(appointment, extras)
    # availDates = appnt.get_available_dates()
    # availTimes = appnt.get_available_times(update_appointment=appointment)
    
    # print(availDates)
    # appnt.dateTime = datetime.strptime(availDates[0].strftime('%Y%m%d'), '%Y%m%d')

    appointment_status = AppointmentStatus.objects.filter(salonAcc=salonAcc)
    active_apps = False
    for actappnt in appnts:
        if actappnt != appointment:
            if not actappnt.status:
                active_apps = True
                break
    appointment = get_object_or_404(Appointment, pk=pk, salonAcc=salonAcc)
    context = {
        'appointment':appointment,  
        'customers':customers,
        'serviceblocks':serviceblocks,
        'extraservices':extraservices,
        'appnts':appnts,
        'appointment_status':appointment_status,
        'active_apps':active_apps,
        'prefer_date':appointment.dateTime.date,
        'prefer_time':appointment.dateTime,
        'stylists':stylists,
        'salonAcc':salonAcc,
        'locker':locker

        
    }

    if request.method == 'POST':
        req = request.POST
        # salonAcc = request.user.salonAcc
        if 'update_status' in req:
            if req['appointment_status']:

                # appointment = Appointment.objects.get(pk=pk, salonAcc=salonAcc)
                appointment.status = AppointmentStatus.objects.get(pk=req['appointment_status'], salonAcc=salonAcc)
                appointment.save()
        # rev = reverse('appointments')
        # rev = '{}?viewdate={}'.format(rev, appDate)        
        # return HttpResponseRedirect(rev)
            messages.success(request, 'Appointments status updated')
            return render(request, 'customers/appointment_update_form.html', context)
        if 'delete' in req:
            for key in req:
                if key.isdigit():
                    appnts = Appointment.objects.get(pk=key, salonAcc=salonAcc)
                    appnts.delete()
            appnts = Appointment.objects.filter(customer=appointment.customer, salonAcc=salonAcc).exclude(pk=pk)
            active_apps = False
            for actappnt in appnts:
                if actappnt != appointment:
                    if not actappnt.status:
                        active_apps = True
                        break

            context['appnts'] = appnts
            context['active_apps'] = active_apps
            context['salonAcc'] = salonAcc
            datetime.s

            messages.success(request, 'Appointments deleted')
            return render(request, 'customers/appointment_update_form.html', context)
        if 'confirm' in req:
            current_app = get_object_or_404(Appointment, pk=req['current_appointment'])
            waiting_apps = TemplateAppointment.objects.filter(salonAcc=salonAcc, waitFrom__lte=current_app.dateTime, waitTo__gte=current_app.dateTime)
            print(waiting_apps)
            cancel_time = current_app.dateTime.strftime('%H:%M:%S %A %d-%m-%Y')
            for _appnt in waiting_apps:
                _appnt.send_notify(f'{salonAcc.salonName}: We have cancelation at {cancel_time}. Please go to https://{salonAcc.website}/appointment-confirm/?id={_appnt.appoinmentID} to book your appointment. Thank you')
            current_app.delete()
            return HttpResponseRedirect(reverse('appointments'))
        if 'update_appointment' in req:
            apnt_time = 0
            service = ServiceBlock.objects.filter(pk=req["service"], salonAcc=salonAcc).first()
            

            custm = appointment.customer
            

            appntDateTime = datetime.strptime(req['time'], "%Y-%m-%d %H:%M:%S")
            temp_appnt = TempAppointment(customer=custm,
                                        salonAcc=salonAcc,
                                        dateTime=appntDateTime,
                                        notice=req['notice'],
                                        service=service,
                                        )
            temp_appnt.temp_extras = []
            for extra in extraservices:
                if extra.name in req:
                    temp_appnt.temp_extras.append(extra)
            if req['stylist']:
                temp_appnt.stylist = SalonStylist.objects.filter(salonAcc=salonAcc, pk=req['stylist']).first()
            appointment = temp_appnt.save_appointment(current_appointment=appointment)
            if appointment:
                    # appointment = resp['message']
                extraservicestr = ''
                for extra in appointment.extras.all():
                    extraservicestr += (extra.name + ' ')
            if 'send_sms' in req:
                if appointment.customer.mobile:
                    cancel_mes = 'To cancel go to. https://{}/appointment-cancel/?id={}'.format(salonAcc.website, appointment.cancelID)
                    message = '{}: Your appointment at {} has been successfully booked. {}'.format(salonAcc.salonName, datetime.strptime(req['time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M %A %d-%m-%Y'), cancel_mes)
                    
                    if len(message) <= 160:
                        
                        queueMSM(salonAcc, message, appointment.customer.mobile)
                    else:
                        message = '{}: Your appointment at {} has been successfully booked.'.format(salonAcc.salonName, datetime.strptime(req['time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M %A %d-%m-%Y'))
                        queueMSM(salonAcc, message, appointment.customer.mobile)
                        cancel_mes = '{}: To cancel please follow the link. https://{}/appointment-cancel/?id={}'.format(salonAcc.salonName, salonAcc.website, appointment.cancelID)
                        queueMSM(salonAcc, cancel_mes, appointment.customer.mobile)
    
            rev = reverse('appointments')
            rev = '{}appointment/update/{}'.format(rev, appointment.pk)
            return HttpResponseRedirect(rev)


            

    else:

        return render(request, 'customers/appointment_update_form.html', context)


def template_app_date_check(request):
    reqst = request
    salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
    from customers.models import AvailableTimes


    if reqst.GET.get('prefer_time'):
        prefer_time = datetime.strptime(reqst.GET.get('prefer_time'), "%Y-%m-%d %H:%M:%S")
        prefer_date = prefer_time.date()
    else:
        prefer_time = None
        prefer_date = None

    
    

    service = get_object_or_404(ServiceBlock, salonAcc=salonAcc, pk=reqst.GET.get('service'))
    if 'stylist' in reqst.GET:
        if reqst.GET.get('stylist'):
            stylist = get_object_or_404(SalonStylist, pk=reqst.GET.get('stylist'))
            temp_appnt = TempAppointment(salonAcc=salonAcc, stylist=stylist, service=service)
        else:
            temp_appnt = TempAppointment(salonAcc=salonAcc, service=service)
    else:
        temp_appnt = TempAppointment(salonAcc=salonAcc, service=service)
    temp_appnt.temp_extras = []
    for extra in ExtraServiceBlock.objects.filter(salonAcc=salonAcc):
        if extra.name in reqst.GET:
            temp_appnt.temp_extras.append(extra)
    logger.debug(temp_appnt.temp_extras)
    if reqst.GET.get('current_appointment'):
        current_appointment = get_object_or_404(Appointment, salonAcc=salonAcc, pk=reqst.GET.get('current_appointment'))
        avaiable_days = temp_appnt.get_available_days(current_appointment=current_appointment)
    else:
        avaiable_days = temp_appnt.get_available_days()
    days = []
    for day in avaiable_days:
        days.append(day)
    days = list(dict.fromkeys(days))                
    days.sort()

    # if temp_appnt.service.equipment_length:
    #     if reqst.GET.get('current_appointment'):
    #         current_appointment = get_object_or_404(Appointment, salonAcc=salonAcc, pk=reqst.GET.get('current_appointment'))
    #         ped_avaiable_days = temp_appnt.get_ped_available_days(current_appointment=current_appointment)
    #     else:
    #         ped_avaiable_days = temp_appnt.get_ped_available_days()
    #     ped_avaiable_days = list(dict.fromkeys(ped_avaiable_days))
    #     logger.debug(f'ped_avaiable_days {ped_avaiable_days}')
    #     ped_day = []
    #     for day in days:
    #         if day in ped_avaiable_days:
    #             ped_day.append(day)
    #     days = ped_day


    
    return JsonResponse({'days':days, 'prefer_date':prefer_date})
    
from .models import AvailableTimesCache, PedChairAvailablesCache, ExcetionLogs, PedicureChairs, SalonEquipment
import traceback
import math
def template_app_time_check(request):
    try:
        # print(dir(cache))
        reqst = request
        salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
        
        if reqst.GET.get('prefer_time'):
            prefer_time = datetime.strptime(reqst.GET.get('prefer_time'), "%Y-%m-%d %H:%M:%S")

        else:
            prefer_time = None
        if request.user.is_authenticated:
            salonAcc = reqst.user.salonAcc
        else:
            salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
        if 'service' in reqst.GET:
            service = get_object_or_404(ServiceBlock, salonAcc=salonAcc, pk=reqst.GET.get('service'))
            length = service.length
            for extra in ExtraServiceBlock.objects.filter(salonAcc=salonAcc):
                if extra.name in reqst.GET:
                    length += extra.length
            slots_required = math.ceil(length/15)
        date = datetime.strptime(reqst.GET.get('date'), '%Y-%m-%d')
        
        if reqst.GET.get('current_appointment'):        
            currentAppointment = get_object_or_404(Appointment, salonAcc=salonAcc, pk=reqst.GET.get('current_appointment'))
        else:
            currentAppointment = None
        # print('service.pedicure_chair_length', service.pedicure_chair_length)



        if reqst.GET.get('stylist'):
            stylist = get_object_or_404(SalonStylist, salonAcc=salonAcc, pk=reqst.GET.get('stylist'))
            allStylistAvailableSlots = []

            availables = AvailableTimesCache(date=date, stylist=stylist, salonAcc=salonAcc)
            availables.currentAppointment = currentAppointment
            stylistAvailableSlots = availables.getAppointmentAvailable(slots_required)

            allStylistAvailableSlots.append(stylistAvailableSlots)
        else:

            allStylistAvailableSlots = []
            stylists = SalonStylist.objects.filter(salonAcc=salonAcc)
            for stylist in stylists:
                availables = AvailableTimesCache(date=date, stylist=stylist, salonAcc=salonAcc)
                availables.currentAppointment = currentAppointment
                stylistAvailableSlots = availables.getAppointmentAvailable(slots_required)

                allStylistAvailableSlots.append(stylistAvailableSlots)
        stylistAvailabletimes = []
        for stylistAvailable in allStylistAvailableSlots:
            
            stylistAvailabletimes += stylistAvailable['availables']
        stylistAvailabletimes = list(dict.fromkeys(stylistAvailabletimes))                
        stylistAvailabletimes.sort()
        if service.pedicure_chair_length:
            chairAvailabletimes = []
            pedicure_chair_length = service.pedicure_chair_length
            chair_slots_required = math.ceil(pedicure_chair_length/15)
            allPedChairAvailableSlots = []
            chairs = PedicureChairs.objects.filter(salonAcc=salonAcc)
            if len(chairs) != 0:
                for chair in chairs:
                    availables = PedChairAvailablesCache(date=date, chair=chair, salonAcc=salonAcc)
                    availables.currentAppointment = currentAppointment
                    chairAvailableSlots = availables.getAppointmentAvailable(chair_slots_required)

                allPedChairAvailableSlots.append(chairAvailableSlots)
            # equipmentAvailabletimes = [equipmentAvailable['availables'] for equipmentAvailable in allEquipmentAvailableSlots ]

                for chairAvailable in allPedChairAvailableSlots:
                    
                    chairAvailabletimes += chairAvailable['availables']
                chairAvailabletimes = list(dict.fromkeys(chairAvailabletimes))                
                chairAvailabletimes.sort()

            availabletimes = [available for available in stylistAvailabletimes if available in chairAvailabletimes]
        else:
            availabletimes = stylistAvailabletimes
        context = {

            "error":0,
            'availabletimes':availabletimes,

            # 'allStylistAvailableSlots':allStylistAvailableSlots,
            'prefer_time':prefer_time,
    
        }
        # if service.pedicure_chair_length:
        #     context['chairAvailabletimes'] = chairAvailabletimes
        return JsonResponse(context)
    except Exception as e:
        ExcetionLogs.objects.create(module=( __name__ ), dateTime=timezone.now(), exception=f'{e} {"".join(traceback.format_tb(e.__traceback__))}')
        # logger.exception('Exception getCurrentAppointmentSlots cache')
        return JsonResponse({"error":-1, "availabletimes":[]})

def old_template_app_time_check(request):
    reqst = request
    salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
    
    if reqst.GET.get('prefer_time'):
        prefer_time = datetime.strptime(reqst.GET.get('prefer_time'), "%Y-%m-%d %H:%M:%S")

    else:
        prefer_time = None
    if request.user.is_authenticated:
        salonAcc = reqst.user.salonAcc
    else:
        salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
    if 'service' in reqst.GET:
        service = get_object_or_404(ServiceBlock, salonAcc=salonAcc, pk=reqst.GET.get('service'))
    if reqst.GET.get('stylist'):
        stylist = get_object_or_404(SalonStylist, salonAcc=salonAcc, pk=reqst.GET.get('stylist'))
        temp_appnt = TempAppointment(salonAcc=salonAcc, stylist=stylist, service=service)
    else:
        temp_appnt = TempAppointment(salonAcc=salonAcc, service=service)
    date = datetime.strptime(reqst.GET.get('date'), '%Y-%m-%d')

    temp_appnt.temp_extras = []
    for extra in ExtraServiceBlock.objects.filter(salonAcc=salonAcc):
        if extra.name in reqst.GET:
            temp_appnt.temp_extras.append(extra)
    # logger.debug(temp_appnt.temp_extras)
    if reqst.GET.get('current_appointment'):
        
        current_appointment = get_object_or_404(Appointment, salonAcc=salonAcc, pk=reqst.GET.get('current_appointment'))
        availabletimes = temp_appnt.get_available_times(date=date, current_appointment=current_appointment)
        print(f'current app {current_appointment}')
    else:
        availabletimes = temp_appnt.get_available_times(date=date)
    availabletimes = list(dict.fromkeys(availabletimes))                
    availabletimes.sort()
    if temp_appnt.service.equipment_length:
        if reqst.GET.get('current_appointment'):
            current_appointment = get_object_or_404(Appointment, salonAcc=salonAcc, pk=reqst.GET.get('current_appointment'))
            ped_availabletimes = temp_appnt.get_ped_available_times(date=date, current_appointment=current_appointment)
        else:
            ped_availabletimes = temp_appnt.get_ped_available_times(date=date)
        
        ped_availabletimes = list(dict.fromkeys(ped_availabletimes))
        logger.debug(f'ped available times {ped_availabletimes}')
        ped_times = []
        for time in availabletimes:
            if time in ped_availabletimes:
                ped_times.append(time)
        availabletimes = ped_times

    context = {

        'availabletimes':availabletimes,

        'prefer_time':prefer_time,
 
    }
    return JsonResponse(context)

def waiting_list_times(request):
    reqst = request
    salonAcc = get_object_or_404(SalonAccount, website=reqst.META['HTTP_HOST'])
    if request.GET.get('waitting_date'):
        _date = datetime.strptime(request.GET.get('waitting_date'), '%Y-%m-%d').date()
        waitting_times =[]
        def openingTime(_date, salonAcc):
            if SpecialOpenTime.objects.filter(salonAcc=salonAcc, date=_date):
                return SpecialOpenTime.objects.filter(salonAcc=salonAcc, date=_date)
            if not ClosedDay.objects.filter(salonAcc=salonAcc, date=_date):
                return OpenTimes.objects.filter(day=_date.weekday(), salonAcc=salonAcc).first()
            else:
                logger.debug('Close day')
                return OpenTimes.objects.filter(day=_date.weekday(), salonAcc=salonAcc).first()
        openingTime = openingTime(_date, salonAcc)

        _time = datetime.strptime('{} {}'.format(request.GET.get('waitting_date'), openingTime.openTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        closed_time = datetime.strptime('{} {}'.format(request.GET.get('waitting_date'), openingTime.closeTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        while _time <= closed_time:
            str_time = _time
            waitting_times.append(_time.strftime('%H:%M:%S'))
            _time += timedelta(minutes=15)

        context = {
            'waitting_times':waitting_times,
        }
        return JsonResponse(context)
            # return render(request, 'customers/waitting_times_ajax.html', context)

def services(request):
    data = {

    }
    extrasevs = ExtraServiceBlock.objects.all()
    sevs = ServiceBlock.objects.all()
    data['services'] = []
    for ser in sevs:
        data['services'].append(ser.name)
    data['extraServices'] = []
    for extser in extrasevs:
        data['extraServices'].append(extser.name)
    return JsonResponse(data)

from django.views.decorators.csrf import csrf_exempt

@login_required
@salon_account_check
def callerID(request):
    reqst = request
    if reqst.method == 'GET':
        obj_callerIDs = CallerID.objects.all()
        callerIDs = []
        for ID in obj_callerIDs:
            callerIDs.append(ID.number)
        if callerID:
            data = {
                'callerID':callerIDs
            }
        else:
            data = {
                'callerID':None
            }
        return JsonResponse(data)

@csrf_exempt
def push_callerID(request):
    reqst = request
    
        
    if reqst.method == 'POST':
        if 'delete' in reqst.POST:
            CallerID.objects.filter(number=reqst.POST['callerID']).delete()
            return HttpResponse()
        if reqst.POST['key'] == 'jfdsjfhajfjasfsah3742rew7hje':
            # callerID = CallerID.objects.first()
            # if callerID:
            #     callerID.number = reqst.POST['callerID']
            #     callerID.save()
            # else:
            CallerID(number=reqst.POST['callerID']).save()
            return HttpResponse()
    else:
        return HttpResponseForbidden()

@csrf_exempt
def push_callerID_1(request):
    reqst = request
    if reqst.POST['key'] != 'jfdsjfhajfjasfsah3742rew7hje':
        return HttpResponseNotFound()
    if reqst.method == 'POST':
        callerID = CallerID.objects.first()
        if callerID:
            callerID.number = reqst.POST['callerID']
            callerID.save()
        else:
            CallerID(number=reqst.POST['callerID']).save()
            
        return HttpResponse()

@login_required
@salon_account_check
def test_login(request):
    return HttpResponse('login ok')


@login_required
def read_smss(request):
    sms = SMS()
    resp = sms.read_all_sms()
    return HttpResponse(resp)

@login_required
def delete_smss(request):
    sms = SMS()
    resp = sms.delete_read_sms()
    return HttpResponse(resp)

@login_required
@salon_account_check
def appointments_json(request):
    reqst = request
    salonAcc = reqst.user.salonAcc
    if not salonAcc:
        return HttpResponseRedirect(reverse('salon-account'))
    closed = False
    stylists = SalonStylist.objects.filter(salonAcc=salonAcc)
    if reqst.method == 'GET':
        if not reqst.GET.get('viewdate'):
            viewdate = datetime.today()
        elif reqst.GET.get('viewdate'):
            viewdate = datetime.strptime(reqst.GET.get('viewdate'), '%Y-%m-%d')
        if SpecialOpenTime.objects.filter(date=viewdate, salonAcc=salonAcc):
            # print('specila openday')
            closed = False
            opening_time = SpecialOpenTime.objects.filter(date=viewdate, salonAcc=salonAcc).first()
        elif not ClosedDay.objects.filter(date=viewdate, salonAcc=salonAcc).first():
            # print(' not close day')
            opening_time = OpenTimes.objects.filter(salonAcc=salonAcc, day=viewdate.weekday()).first()
            closed = not (opening_time.openTime and opening_time.closeTime)

        else:
            closed = True
    # print(closed)
 


        data = {


            # 'weekday': weekday,
            'stylists': list(stylists),
            'viewdate':viewdate,
            'closed':closed,
            'salonAcc':salonAcc,

        }

        return JsonResponse(context)
    else:
        context = {
            'viewdate':viewdate,
            'closed':closed,
            'salonAcc':salonAcc

        }
        return render(request, 'customers/appointments.html', {'closed':closed})

