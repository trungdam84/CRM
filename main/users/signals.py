from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CustomUser, SalonAccount
from customers.models import OpenTimes

from pathlib import Path
import logging, os
from datetime import datetime
from django.conf import settings




logs_path = os.path.join(Path(settings.BASE_DIR).parents[0], 'logs')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler(os.path.join(logs_path, 'customers.log'))

file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


logger.debug('Signals has imported')


@receiver(post_save, sender=SalonAccount)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # print(instance)
        openTime = datetime.strptime('09:00', '%H:%M').time()
        closeTime = datetime.strptime('18:00', '%H:%M').time()
        for i in range(0,7):
            OpenTimes(day=i, salonAcc=instance, openTime='09:00', closeTime=closeTime).save()



