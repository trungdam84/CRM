from time import sleep
import serial
import logging, os
from pathlib import Path

from django.conf import settings

logs_path = os.path.join(Path(settings.BASE_DIR).parents[0], 'logs')

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler(os.path.join(logs_path, 'usb.log'))

file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)
# set a format which is simpler for console use

console.setFormatter(formatter)
# add the handler to the root logger
logger.addHandler(console)
logger.addHandler(file_handler)


# from curses import ascii

'''Run this file in your shell, the aim for this script is to try and allow you to
    send, read and delete messages from python, after playing around with this for a while i have
    realised that the most importain thing is good signal strength at the modem. For a full list of
    fuctions that a GSM modem is capable of google Haynes AT+ commands

    I have put the sleep function into many of the functions found within this script as it give the modem time
    to receive all the messages from the Mobile Network Operators servers'''
class SMS(object):
    
    def __init__(self):
    #set serial
        self.ser = serial.Serial()
        
        ##Set port connection to USB port GSM modem 
        self.ser.port = '/dev/ttyUSB0'
        
        ## set older phones to a baudrate of 9600 and new phones and 3G modems to 115200
        ##ser.baudrate = 9600
        self.ser.baudrate = 115200
        self.ser.timeout = 1
        # self.ser.write_timeout = 10
        # self.ser.open()
        # self.ser.write(bytes('AT+CMGF=1\r\n', 'utf-8'))
        ##following line of code sets the prefered message storage area to modem memory
        # self.ser.write(bytes('AT+CPMS="ME","SM","ME"\r\n', 'utf-8'))
    
    
    ## Important understand the difference between PDU and text mode, in PDU istructions are sent to the port as numbers eg: 0,1,2,3,4 and in TEXT mode as text eg: "ALL", "REC READ" etc
    ## following line sets port into text mode, all instructions have to be sent to port as text not number
    ##Important positive responses from the modem are always returned as OK
    
    ##you may want to set a sleep timer between sending texts of a few seconds to help the system process
    
    def sendsms(self, number, text):
        try:
            self.ser.open()
            self.ser.write(bytes('AT+CMGF=1\r\n', 'utf-8'))
            logger.debug(self.ser.readlines())
            logger.debug('AT+CMGF=1\r\n')
            sleep(1)
            self.ser.write(bytes('AT+CSMP=49,167,0,0\r\n', 'utf-8'))
            logger.debug(self.ser.readlines())
            logger.debug('AT+CSMP=49,167,0,0\r\n')
            sleep(1)
            self.ser.write(bytes('AT+CNMI=2,1,0,1,0\r\n', 'utf-8'))
            logger.debug(self.ser.readlines())
            logger.debug('AT+CNMI=2,2,0,1,0\r\n')
            sleep(1)
            self.ser.write(bytes('AT+CMGS="{}"\r\n'.format(number), 'utf-8'))
            logger.debug(self.ser.readlines())
            logger.debug('AT+CMGS="{}"\r\n'.format(number))
            sleep(1)
            self.ser.write(bytes('{}'.format(text), 'utf-8'))
            logger.debug(self.ser.readlines())
            logger.debug('{}'.format(text))
            sleep(1)
            self.ser.write(bytes('\x1A\r\n', 'utf-8'))
            logger.debug(self.ser.readlines())
            logger.debug('\x1A\r\n')
            sleep(1)
            # a = self.ser.readlines()
            self.ser.close()
            sleep(2)
            logger.debug('SMS sent {} {}'.format(number, text))
            return True
        except Exception as e:
            logger.debug(e)
            return False
        # print("Text: {}  \nhas been sent to: {}".format(text, number))
    
    
    def read_all_sms(self):
        self.ser.open()
        self.ser.write(bytes('AT+CMGF=1\r\n', 'utf-8'))
        sleep(5)
        self.ser.write(bytes('AT+CMGL="ALL"\r\n', 'utf-8'))
        sleep(15)
        a = self.ser.readlines()
        print(a)
        z = []
        y = []
        for x in a:
            # x.decode("utf-8")
            if x.startswith(bytes('+CMGL:', 'utf-8')):
                r = a.index(x)
                t = r + 1
                z.append(r)
                z.append(t)
        for x in z:
            y.append(a[x])
    
        ## following line changes modem back to PDU mode
        self.ser.write(bytes('AT+CMGF=0\r\n', 'utf-8'))
        self.ser.close()
        return y
    
    
    def read_unread_sms(self):
        self.ser.write('AT+CMGF=1\r\n')
        sleep(5)
        self.ser.write('AT+CMGL="REC UNREAD"\r\n')
        sleep(15)
        a = ser.readlines()
        z = []
        y = []
        for x in a:
            if x.startswith('+CMGL:'):
                r = a.index(x)
                t = r + 1
                z.append(r)
                z.append(t)
        for x in z:
            y.append(a[x])
    
        ##Following line changed modem back to PDU mode
        self.ser.write('AT+CMGF=0\r\n')
        return y
    
    
    def read_read_sms(self):
        ##returns all unread sms's on your sim card
        self.ser.write('AT+CMGS=1\r\n')
        self.ser.read(100)
        self.ser.write('AT+CMGL="REC READ"\r\n')
        self.ser.read(1)
        a = self.ser.readlines()
        for x in a:
            print(x)
        
    
    
    def delete_all_sms(self):
        ##this changes modem back into PDU mode and deletes all texts then changes modem back into text mode
        self.ser.open()
        self.ser.write(bytes('AT+CMGF=0\r\n', 'utf-8'))
        sleep(5)
        self.ser.write(bytes('AT+CMGD=0,4\r\n', 'utf-8'))
        sleep(5)
        self.ser.write(bytes('AT+CMGF=1\r\n', 'utf-8'))
        self.ser.close()
        return True
    
    
    def delete_read_sms(self):
        ##this changes modem back into PDU mode and deletes read texts then changes modem back into text mode
        self.ser.write(bytes('AT+CMGF=0\r\n', 'utf-8'))
        sleep(1)
        self.ser.write(bytes('AT+CMGD=0,1\r\n', 'utf-8'))
        sleep(1)
        self.ser.write(bytes('AT+CMGF=1\r\n', 'utf-8'))
        self.ser.close()
        return True
    
    
    ##this is an attempt to run ussd commands from the gsm modem
    
    def check_ussd_support(self):
        ##if return from this is "OK" this phone line supports USSD, find out the network operators codes
        self.ser.write('AT+CMGF=0\r\n')
        self.ser.write('AT+CUSD=?\r\n')
        self.ser.write('AT+CMGF=1\r\n')
    
    
    ##This function is an attempt to get your sim airtime balance using USSD mode
    def get_balance(self):
        ##first set the modem to PDU mode, then pass the USSD command(CUSD)=1, USSD code eg:*141# (check your mobile operators USSD numbers)
        ## Error may read +CUSD: 0,"The service you requested is currently not available.",15
        ## default value for <dcs> is 15 NOT 1
        self.ser.open()
        self.ser.write(bytes('AT+CMGF=0\r\n', 'utf-8'))
        self.ser.write(bytes('AT+CUSD=1,*137#,15\r\n', 'utf-8'))
        self.ser.read(1)
        a = self.ser.readlines()
        print(a)

        self.ser.write(bytes('AT+CMGF=1\r\n', 'utf-8'))
        self.ser.close()
        return a

        ##This function is an attempt to send USSD
    def ussd(self, code):
        ##first set the modem to PDU mode, then pass the USSD command(CUSD)=1, USSD code eg:*141# (check your mobile operators USSD numbers)
        ## Error may read +CUSD: 0,"The service you requested is currently not available.",15
        ## default value for <dcs> is 15 NOT 1
        ussd_code = 'AT+CUSD=1,{},15\r\n'.format(code)
        self.ser.open()
        self.ser.write(bytes('AT+CMGF=0\r\n', 'utf-8'))
        self.ser.write(bytes(ussd_code, 'utf-8'))
        self.ser.read(1)
        a = self.ser.readlines()
        # print(a)

        self.ser.write(bytes('AT+CMGF=1\r\n', 'utf-8'))
        self.ser.close()
        return a

    def ussd_sms_check(self):
        ##first set the modem to PDU mode, then pass the USSD command(CUSD)=1, USSD code eg:*141# (check your mobile operators USSD numbers)
        self.ser.write('AT+CMGF=0\r\n')
        self.ser.write('AT+CUSD=1,*141*1#,15\r\n')
        self.ser.read(100)
        a = self.ser.readlines()
        print
        a
        self.ser.write('AT+CMGF=1\r\n')