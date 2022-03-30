from customers.models import OpenTimes, ClosedDay
import calendar
from datetime import datetime, timedelta
from django.shortcuts import redirect, get_object_or_404
from customers.models import PedicureChairs
from pathlib import Path
import logging, os

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

class AvailableTimesMixin():
                
    def get_opening_time(self):

        try:
            if not ClosedDay(salonAcc=self.salonAcc, date=self.date):
                opening_time = OpenTimes.objects.filter(day=self.date.weekday(), salonAcc=self.salonAcc).first()
                return opening_time
            else:
                return OpenTimes(day=self.date.weekday(), salonAcc=self.salonAcc)
        except Exception as e:
            logger.exception('TemplateAppointment get_opening_time error {}'.format(e))
    
    def create_availables_times(self):
        openingTime = self.get_opening_time()
        slot = openingTime.openTime

        while slot <= openingTime.closeTime:
            self.availables.append(slot.strftime('%H-%M-%S'))
            self.ped_availables.append(slot.strftime('%H-%M-%S'))
            slot += timedelta(minutes=15)
        self.save()




 
    