from .models import Appointment, QueueSMS
import datetime, time, threading

def one_day_sms_remider():

    
    while 1:
        if datetime.datetime.now().time() > datetime.datetime.strptime('18:43:00', '%H:%M:%S').time() and datetime.datetime.now().time() < datetime.datetime.strptime('18:43:06', '%H:%M:%S').time():
            print('reminder')
            dt = datetime.datetime.now() + datetime.timedelta(days=1)

            appointments = Appointment.objects.filter(dateTime__range=((datetime.datetime.combine(dt.date(), dt.time().min)), datetime.datetime.combine(dt.date(), dt.time().max)))
            # print(appointments)
            for appointment in appointments:
                if appointment.customer.mobile:
                    cancel_mes = 'To cancel go to. https://{}/appointment-cancel/?id={}'.format(appointment.salonAcc.website, appointment.cancelID)
                    q_sms = QueueSMS(message='{}: This is reminder of your Nails appointment tomorrow at {}. {}'.format(appointment.salonAcc.salonName, appointment.dateTime.time(), cancel_mes), destination=appointment.customer.mobile)
                    q_sms.save()

        time.sleep(5)

smsrmd = threading.Thread(target = one_day_sms_remider, name = 'thread{}'.format('sms one_day_sms_remider loop'), args=())
smsrmd.daemon = True
smsrmd.start()