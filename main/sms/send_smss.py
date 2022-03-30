from customers.models import QueueSMS
from customers.sms_module import SMS
import time, threading


def sendSMS():
    print('SMS module loaded')
    while 1:

        q_sms = QueueSMS.objects.all().order_by('createTime').first()
        # print(q_sms.destination, q_sms.message, 'loaded')
        if q_sms:
            sms = SMS()
            # try:
            if sms.sendsms(q_sms.destination, q_sms.message):

                print(q_sms.destination, q_sms.message, 'sent')
                q_sms.delete()


            # except Exception as e:
            #     print(e)
            # smst = threading.Thread(target = sms.send_sms, name = 'thread{}'.format(destination), args=())
            # smst.daemon = True
            # smst.start()
        #print('sleep')
        time.sleep(5)


smst = threading.Thread(target = sendSMS, name = 'thread{}'.format('sms send loop'), args=())
smst.daemon = True
smst.start()
