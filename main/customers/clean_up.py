from .models import Appointment, NotTurnedUp, Customer, AvailableTimes, AvailableChairTimes
import datetime, threading, time

def app_clean_up():
    while 1:
        # print('clean up loop')
        if datetime.datetime.now().time() > datetime.datetime.strptime("22:59:59", "%H:%M:%S").time() and datetime.datetime.now().time() < datetime.datetime.strptime("23:59:59", "%H:%M:%S").time():
            appointments = Appointment.objects.filter(dateTime__lt=datetime.datetime.now())
            # print(appointments)
            AvailableTimes.objects.filter(date__lt=datetime.datetime.today()).delete()
            AvailableChairTimes.objects.filter(date__lt=datetime.datetime.today()).delete()
            for appointment in appointments:
                # print(type(appointment.status))
            #     if appointment.status.status:
            #         print(appointment.status.status)
                if appointment.status:
                    if appointment.status.status == 'Not turned up':
                        # print('here')
                        NotTurnedUp(salonAcc=appointment.salonAcc, customer=appointment.customer, service=appointment.service, dateTime=appointment.dateTime).save()
            appointments.delete()
        # print(appointments)

        # _time = datetime.datetime.now() + datetime.timedelta(hours=2)
        # appointments = Appointment.objects.filter(dateTime__range=(_time, (_time + datetime.timedelta(minutes=15))))
        # for appointment in appointments:
        #     if appointment.customer.mobile:
        #         q_sms = QueueSMS(message='Creatip: This is remider of your Nails appointment today at {}'.format(appointment.dateTime.time()), destination=appointment.customer.mobile)
        #         q_sms.save()
        #         # print('sent remider', appointment.dateTime)
        time.sleep(3600)



clsup = threading.Thread(target = app_clean_up, name = 'thread{}'.format('app_clean_up loop'), args=())
clsup.daemon = True
clsup.start()