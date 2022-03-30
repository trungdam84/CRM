from .models import Appointment, QueueSMS
import datetime, time, threading, schedule

def sms_remider():
    while 1:
        # print('loop')
        _time = datetime.datetime.now() + datetime.timedelta(hours=2)
        appointments = Appointment.objects.filter(dateTime__range=(_time, (_time + datetime.timedelta(minutes=15))))
        for appointment in appointments:
            if appointment.customer.mobile:
                cancel_mes = 'To cancel go to. https://{}/appointment-cancel/?id={}'.format(appointment.salonAcc.website, appointment.cancelID)
                q_sms = QueueSMS(message='{}: This is reminder of your Nails appointment today at {}. {}'.format(appointment.salonAcc.salonName, appointment.dateTime.time(), cancel_mes), destination=appointment.customer.mobile)
                q_sms.save()
                # print('sent remider', appointment.dateTime)
        time.sleep(60*15)



smsrmd = threading.Thread(target = sms_remider, name = 'thread{}'.format('sms sms_remider loop'), args=())
smsrmd.daemon = True
smsrmd.start()




