import requests
import mysql.connector

import logging, os
import datetime
# from usb_module import USB
import time

logs_path = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler(os.path.join(logs_path, 'send_sms.log'))

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use

console.setFormatter(formatter)
# add the handler to the root logger
logger.addHandler(console)

logger.addHandler(file_handler)

class AndroidSMS():
  def __init__(self, ipadress):
     self.url = "http://{}:8082".format(ipadress)



  def send_sms(self, number, message):
      to = f'\"to\":\"+44{number[1:]}\"'
      message = f'\"message\":\"*0#{message}\"'
      payload = '{' + to + ',' + message + '}'



      headers = {
        'Authorization': '42e7d5d5',
        'Content-Type': 'text/plain'
      }
      try:
          response = requests.request("POST", self.url, headers=headers, data=payload, timeout=10)
          return response.status_code
      except Exception as e:
          logger.exception(e)



# sms = AndroidSMS('192.168.1.239')
#
#
# print(sms.send_sms('07401384305', 'Hello'))





def sendSMS():

    logger.debug('SMS module loaded')

    sms = AndroidSMS('10.10.40.4')

    while 1:
        if datetime.datetime.now().time() > datetime.datetime.strptime('08:00:00', '%H:%M:%S').time() and datetime.datetime.now().time() < datetime.datetime.strptime('08:00:06', '%H:%M:%S').time():
            sms.send_sms('07401384305', 'SMS ok')


        try:
            connection = mysql.connector.connect(host='localhost',
                                                database='salon-crm',
                                                user='root',
                                                password='123456')

            sql_select_Query = "select * from customers_queuesms"
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            # get all records
            records = cursor.fetchall()
            if cursor.rowcount > 0:
                logger.debug("Total number of rows in table: {}".format(cursor.rowcount))

                logger.debug("\nPrinting each row")
            for q_sms in records:

                # try:
                if sms.send_sms(q_sms[2], q_sms[1]) == 200:

                    sql = "DELETE FROM customers_queuesms WHERE id = '{}'".format(q_sms[0])

                    cursor.execute(sql)

                    connection.commit()
                    logger.debug('Sms send {} {}'.format(q_sms[2], q_sms[1]))
                    time.sleep(2)


        except mysql.connector.Error as e:
            logger.exception(e)
        finally:
            if connection.is_connected():
                connection.close()
                cursor.close()
                #logger.info("MySQL connection is closed")

        time.sleep(5)

sendSMS()