from django.db import models
from users.models import SalonAccount
from pathlib import Path
import logging, os
from django.core.cache import cache
from datetime import timedelta, datetime
from django.utils import timezone
from logs.models import ExcetionLogs
import traceback
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


# Create your models here.

class SalonStylist(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    def __str__(self):
        return "{} {}".format(self.firstName, self.lastName)

class SalonEquipment(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    def __str__(self):
        return "{}".format(self.name)



class PedicureChairs(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.name)



class Customer(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    tel = models.CharField(max_length=15, null=True, blank=True)
    address_1 = models.CharField(max_length=50, null=True, blank=True)
    address_2 = models.CharField(max_length=50, null=True, blank=True)
    town = models.CharField(max_length=50, null=True, blank=True)
    postCode = models.CharField(max_length=10, null=True, blank=True)
    notice = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('salonAcc', 'mobile', 'firstName', 'lastName')

    def __str__(self):
        return "{} {}".format(self.firstName, self.lastName ,self.mobile) 

class CustomerSession(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    session = models.CharField(max_length=32)
    expired = models.DateTimeField()


class CustomerNotice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    notice = models.CharField(max_length=250)
    def __str__(self):
        return f'{self.customer} {self.notice}'
    
class CustomerVerify(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    verify_id = models.CharField(max_length=15, unique=True)
    verify_code = models.CharField(max_length=6)
    created = models.DateTimeField(auto_created=True)
    def __str__(self):
        return "{} {}".format(self.customer, self.verify_id ,self.verify_code) 



class CustomerBox(models.Model):

    boxNumber = models.PositiveSmallIntegerField()
    customer = models.OneToOneField(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    lastUsed = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f'{self.boxNumber} {self.lastUsed}'

class StoreLocker(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    boxNumber = models.PositiveSmallIntegerField()
    customer = models.OneToOneField(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    lastUsed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('salonAcc', 'boxNumber')
    def __str__(self):
        return "{}".format(self.boxNumber)

class Service(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    serviceName = models.CharField(max_length=50)
    
    def __str__(self):
        return "{}".format(self.serviceName)

class ServiceBlock(models.Model):
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True)
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    length = models.PositiveSmallIntegerField()
    pedicure_chair_length = models.PositiveSmallIntegerField(null=True, blank=True)
    # pedChair = models.ForeignKey(PedicureChairs, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)



class ExtraServiceBlock(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    length = models.SmallIntegerField()
    frontEnd = models.BooleanField(default=True)
    def __str__(self):
        return "Extra service {} {}".format(self.name, self.length)     

class StylistServiceLength(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    stylist = models.ForeignKey(SalonStylist, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceBlock, on_delete=models.CASCADE)
    length = models.PositiveSmallIntegerField()

class StylistExtraServiceLength(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    stylist = models.ForeignKey(SalonStylist, on_delete=models.CASCADE)
    extrsService = models.ForeignKey(ExtraServiceBlock, on_delete=models.CASCADE)
    length = models.PositiveSmallIntegerField()

class AppointmentStatus(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return str(self.status)


class Appointment(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    dateTime = models.DateTimeField(null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    status = models.ForeignKey(AppointmentStatus, on_delete=models.SET_NULL, null=True, blank=True)
    # status = models.ForeignKey(AppointmentStatus, on_delete=models.SET_NULL, null=True, blank=True)
    stylist = models.ForeignKey(SalonStylist, on_delete=models.CASCADE)
    special = models.BooleanField(default=False)
    notice = models.TextField(blank=True)
    service = models.ForeignKey(ServiceBlock, on_delete=models.CASCADE)

    extras = models.ManyToManyField(ExtraServiceBlock, blank=True)
    chair = models.ForeignKey(PedicureChairs, on_delete=models.SET_NULL, null=True, blank=True)
    cancelID = models.CharField(max_length=50, unique=True)
    STATUS_CHOICES = (
    (0, 'Pendding'),
    (1, 'Processing'),
    (2, 'Done'),
    (3, 'Cancelled'),
    (4, 'Not Turned Up'),
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)

    class Meta:
        unique_together = ['customer', 'dateTime', 'service', 'salonAcc', 'stylist']

    def __str__(self):
        return '{}'.format(str(self.salonAcc))


class ClosedDay(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    date = models.DateField()
    def __str__(self):
        return '{}'.format(str(self.date))

class WeeklyCloseDay(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    DAY_CHOICES = (
    (0, 'Moday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
    )
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    def __str__(self):
        DAY_CHOICES = (
            (0, 'Moday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
            )
        for day in DAY_CHOICES:
            if self.day in day:
                closedDay = day[1]
        return str(closedDay)   

class SpecialOpenTime(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    date = models.DateField()
    openTime = models.TimeField()
    closeTime = models.TimeField()

    

    class Meta:
        verbose_name = "Special OpenTime"
        verbose_name_plural = "Special OpenTimes"

    def __str__(self):
        return str(self.date)

class GenaralOpenTime(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    openTime = models.TimeField()
    closeTime = models.TimeField()

    def __str__(self):
        return "Open {} Colsed {}".format(str(self.openTime), str(self.closeTime))

class OpenTimes(models.Model):
    DAY_CHOICES = (
    (0, 'Moday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
    )
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    openTime = models.TimeField(null=True, blank=True)
    closeTime = models.TimeField(null=True, blank=True)
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    def __str__(self):
        return "Day {} Open {} Colsed {}".format(str(self.day), str(self.openTime), str(self.closeTime))

class QueueSMS(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE, null=True)
    message = models.CharField(max_length=159)
    destination = models.CharField(max_length=13)
    createTime = models.DateTimeField(auto_now=True)

    
class TemplateAppointment(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    appoinmentID = models.CharField(max_length=25)
    appoinmentOTP = models.CharField(max_length=4)
    appoinmentFName = models.CharField(max_length=25)
    appoinmentLName = models.CharField(max_length=25)
    appoinmentMobile = models.CharField(max_length=12)
    createdTime = models.DateTimeField(auto_now_add=True)
    appoinmentService = models.ForeignKey(ServiceBlock, on_delete=models.SET_NULL, null=True, blank=True)
    appoinmentEXtra = models.ManyToManyField(ExtraServiceBlock, blank=True)
    verified = models.BooleanField(default=False)
    otpResend = models.DateTimeField(null=True, blank=True)
    notice = models.CharField(null=True, blank=True, max_length=250)
    waitFrom = models.DateTimeField(null=True)
    waitTo = models.DateTimeField(null=True)
    updatedTime = models.DateTimeField(auto_now=True)
    notified = models.BooleanField(default=False)

    def send_notify(self, message):
        # print(message)
        if not self.notified:

            qsms = QueueSMS(salonAcc=self.salonAcc, message=message, destination=self.appoinmentMobile)
            qsms.save()
            # self.notified = True
            self.save()




class CallerID(models.Model):
    number = models.CharField(max_length=15)





from django.core.cache import cache
class TimesCache(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    date = models.DateField()
    currentAppointment = None

    def get_opening_time(self):
        if SpecialOpenTime.objects.filter(salonAcc=self.salonAcc, date=self.date):
            return SpecialOpenTime.objects.filter(salonAcc=self.salonAcc, date=self.date).first()
        if not ClosedDay.objects.filter(salonAcc=self.salonAcc, date=self.date):
            opening_time = OpenTimes.objects.filter(day=self.date.weekday(), salonAcc=self.salonAcc).first()
            logger.debug('Open day')
            return opening_time
        else:
            logger.debug('Close day')
            return OpenTimes.objects.filter(day=self.date.weekday(), salonAcc=self.salonAcc).first()



    def availables_times(self):
        openingTime = self.get_opening_time()
        if openingTime.openTime and openingTime.closeTime:
            logger.debug(openingTime)
            slot_str = '{} {}'.format(self.date.strftime('%Y-%m-%d'), openingTime.openTime.strftime('%H:%M:%S'))
            slot = datetime.strptime(slot_str, '%Y-%m-%d %H:%M:%S')
            availables = []
            while slot.time() < openingTime.closeTime:
                availables.append(slot)
                slot += timedelta(minutes=15)
            for slot in self.unavailable_times():
                try:
                    availables.remove(slot)
                except Exception as e:
                    logger.exception(e)
        return availables

class PedChairAvailablesCache(TimesCache):
    chair = models.ForeignKey(PedicureChairs, on_delete=models.CASCADE)
    def setAvailableCache(self):

        availables = self.availables_times()
        # print('set available cache', availables, self.stylist)
        cache.delete(f'{self.salonAcc.pk}_{self.chair.pk}_{self.date.strftime("%m/%d/%Y")}_chair_availables')
        cache.set(f'{self.salonAcc.pk}_{self.chair.pk}_{self.date.strftime("%m/%d/%Y")}_chair_availables', availables)
        return {"error":'0',"availables":availables, 'chair':self.chair.pk, 'cached':False}
        

    def deleteAvailableCache(self):       
        cache.delete(f'{self.salonAcc.pk}_{self.chair.pk}_{self.date.strftime("%m/%d/%Y")}_chair_availables')

    def getCurrentAppointmentTimeSlots(self):
        if self.currentAppointment:
            try:
                current_slots = []
                current_app_length = self.currentAppointment.service.length
                for extra in self.currentAppointment.extras.all():
                    current_app_length += extra.length
                slot = self.currentAppointment.dateTime
                while slot < self.currentAppointment.dateTime + timedelta(minutes=current_app_length):
                    current_slots.append(slot)
                    slot += timedelta(minutes=15)
                return {"error":0, "CurrentSlots":current_slots, 'chair':self.currentAppointment.chair.pk}
            except Exception as e:
                ExcetionLogs.objects.create(module=( __name__ ), dateTime=timezone.now(), exception=f'{e} {"".join(traceback.format_tb(e.__traceback__))}')
                # logger.exception('Exception getCurrentAppointmentSlots cache')
                return {"error":-1, "CurrentSlots":[], 'chair':self.currentAppointment.chair.pk}
        else:
            return {"error":0, "CurrentSlots":[], 'chair':None}

    def getAvailableCache(self):

        currentSlots = self.getCurrentAppointmentTimeSlots()
        if currentSlots["error"] == 0:
            availables = cache.get(f'{self.salonAcc.pk}_{self.chair.pk}_{self.date.strftime("%m/%d/%Y")}_chair_availables')
            # print('current slots', currentSlots)
            # print('get available cache')
            if availables != None:
                if currentSlots['chair'] == self.chair.pk:
                    availables += currentSlots["CurrentSlots"]
                    availables.sort()
                return {"error":0,"availables":availables, 'chair':self.chair.pk, 'cached':True}
            else:
                availables = self.setAvailableCache()["availables"]
                if availables != None:
                    if currentSlots['chair'] == self.chair.pk:
                        availables += currentSlots["CurrentSlots"]
                        availables.sort()
                return {"error":0,"availables":availables, 'chair':self.chair.pk, 'cached':False}


    def getAppointmentAvailable(self, slots_required, *args, **kwargs):
        

        checked_available_times = []
        availableSlots = self.getAvailableCache()

        # print(availableSlots)
        if availableSlots["error"] == 0:
            chairAvailables = availableSlots['availables']

            for i in range(len(chairAvailables)-1, -1, -1):                    
                if i == len(chairAvailables)-1:
                    
                    k = 1
                    # logger.debug('k {} lots required {}'.format(k, appmt_slots_required))
                elif chairAvailables[i+1] - chairAvailables[i] <= timedelta(minutes=15):
                    k += 1
                    # logger.debug(datetime.strptime(available_slots[i+1], '%Y-%m-%d %H:%M:%S') - datetime.strptime(available_slots[i], '%Y-%m-%d %H:%M:%S'))
                    
                    # logger.debug('k {} lots required {}'.format(k, appmt_slots_required))

                    if k >= int(slots_required):
                        # logger.debug(f'{available_slots[i+1]},  {available_slots[i]} k {k} checked_available_times {checked_available_times}')
                        checked_available_times.append(chairAvailables[i])

                else:
                    k = 1
            checked_available_times.sort()
            return {"error":0, "availables":checked_available_times, 'availableSlots':availableSlots}
        else:
            return {"error":-1, "availables":checked_available_times,'availableSlots':availableSlots}



    def unavailable_times(self):
        unavailable_times = []
        openingTime = self.get_opening_time()
        opentime = datetime.combine(self.date, openingTime.openTime)
        closetime = datetime.combine(self.date, openingTime.closeTime)
        exiting_appntms = Appointment.objects.filter(salonAcc=self.salonAcc, chair=self.chair, dateTime__range=(opentime, closetime))
        for exiting_appmt in exiting_appntms:
            check_slot = exiting_appmt.dateTime

            app_length = exiting_appmt.service.length
            for extra in exiting_appmt.extras.all():
                app_length += extra.length
            while check_slot < exiting_appmt.dateTime + timedelta(minutes=app_length):                
                unavailable_times.append(check_slot)
                check_slot += timedelta(minutes=15)
        logger.debug(f'unavailable times {unavailable_times}')
        return unavailable_times


class AvailableTimesCache(TimesCache):
    stylist = models.ForeignKey(SalonStylist, on_delete=models.CASCADE)
    chair = models.ForeignKey(PedicureChairs, on_delete=models.SET_NULL, null=True, blank=True)

    def setAvailableCache(self):

        availables = self.availables_times()
        # print('set available cache', availables, self.stylist)
        cache.delete(f'{self.salonAcc.pk}_{self.stylist.pk}_{self.date.strftime("%m/%d/%Y")}_availables')
        cache.set(f'{self.salonAcc.pk}_{self.stylist.pk}_{self.date.strftime("%m/%d/%Y")}_availables', availables)
        return {"error":'0',"availables":availables, 'stylist':self.stylist.pk, 'cached':False}
        
    def deleteAvailableCache(self):       
        cache.delete(f'{self.salonAcc.pk}_{self.stylist.pk}_{self.date.strftime("%m/%d/%Y")}_availables')

    def getAvailableCache(self):

        currentSlots = self.getCurrentAppointmentTimeSlots()
        if currentSlots["error"] == 0:
            availables = cache.get(f'{self.salonAcc.pk}_{self.stylist.pk}_{self.date.strftime("%m/%d/%Y")}_availables')
            # print('current slots', currentSlots)
            # print('get available cache')
            if availables != None:
                    if currentSlots['stylist'] == self.stylist.pk:
                        availables += currentSlots["CurrentSlots"]
                        availables.sort()
                    return {"error":0,"availables":availables, 'stylist':self.stylist.pk, 'cached':True}
            else:
                availables = self.setAvailableCache()["availables"]
                if availables != None:
                    if currentSlots['stylist'] == self.stylist.pk:
                        availables += currentSlots["CurrentSlots"]
                        availables.sort()
                    return {"error":0,"availables":availables, 'stylist':self.stylist.pk, 'cached':False}


    
    def getCurrentAppointmentTimeSlots(self):
        if self.currentAppointment:
            try:
                current_slots = []
                current_app_length = self.currentAppointment.service.length
                for extra in self.currentAppointment.extras.all():
                    current_app_length += extra.length
                slot = self.currentAppointment.dateTime
                while slot < self.currentAppointment.dateTime + timedelta(minutes=current_app_length):
                    current_slots.append(slot)
                    slot += timedelta(minutes=15)
                return {"error":0, "CurrentSlots":current_slots, 'stylist':self.currentAppointment.stylist}
            except Exception as e:
                ExcetionLogs.objects.create(module=( __name__ ), dateTime=timezone.now(), exception=f'{e} {"".join(traceback.format_tb(e.__traceback__))}')
                # logger.exception('Exception getCurrentAppointmentSlots cache')
                return {"error":-1, "CurrentSlots":[], 'stylist':self.currentAppointment.stylist.pk}
        else:
            return {"error":0, "CurrentSlots":[], 'stylist':None}
    


    def getAppointmentAvailable(self, slots_required, *args, **kwargs):
        

        checked_available_times = []
        availableSlots = self.getAvailableCache()

        # print(availableSlots)
        if availableSlots["error"] == 0:
            stylistAvailables = availableSlots['availables']

            for i in range(len(stylistAvailables)-1, -1, -1):                    
                if i == len(stylistAvailables)-1:
                    
                    k = 1
                    # logger.debug('k {} lots required {}'.format(k, appmt_slots_required))
                elif stylistAvailables[i+1] - stylistAvailables[i] <= timedelta(minutes=15):
                    k += 1
                    # logger.debug(datetime.strptime(available_slots[i+1], '%Y-%m-%d %H:%M:%S') - datetime.strptime(available_slots[i], '%Y-%m-%d %H:%M:%S'))
                    
                    # logger.debug('k {} lots required {}'.format(k, appmt_slots_required))

                    if k >= int(slots_required):
                        # logger.debug(f'{available_slots[i+1]},  {available_slots[i]} k {k} checked_available_times {checked_available_times}')
                        checked_available_times.append(stylistAvailables[i])

                else:
                    k = 1
            checked_available_times.sort()
            return {"error":0, "availables":checked_available_times, 'availableSlots':availableSlots}
        else:
            return {"error":-1, "availables":checked_available_times,'availableSlots':availableSlots}



    def unavailable_times(self):
        unavailable_times = []
        openingTime = self.get_opening_time()
        opentime = datetime.combine(self.date, openingTime.openTime)
        closetime = datetime.combine(self.date, openingTime.closeTime)
        exiting_appntms = Appointment.objects.filter(salonAcc=self.salonAcc, stylist=self.stylist, dateTime__range=(opentime, closetime))
        for exiting_appmt in exiting_appntms:
            check_slot = exiting_appmt.dateTime

            app_length = exiting_appmt.service.length
            for extra in exiting_appmt.extras.all():
                app_length += extra.length
            while check_slot < exiting_appmt.dateTime + timedelta(minutes=app_length):                
                unavailable_times.append(check_slot)
                check_slot += timedelta(minutes=15)
        logger.debug(f'unavailable times {unavailable_times}')
        return unavailable_times
    

    # def get_max_length(self, *args, **kwargs):
    #     i = 0
    #     self.maxLength = 0
    #     if self.availables:
    #         availables = self.availables.split(',') 
    #         self.maxLength = 15                    
    #         check_slot = datetime.strptime(availables[0], '%Y-%m-%d %H:%M:%S')
    #         for k in range(0, len(availables)):
    #             if k == 0:
    #                 i +=1
    #             else:
    #                 slot_time = datetime.strptime(availables[k], '%Y-%m-%d %H:%M:%S')
    #                 check_slot = datetime.strptime(availables[k-1], '%Y-%m-%d %H:%M:%S')            
    #                 if slot_time - check_slot <= timedelta(minutes=15):
    #                     i += 1
    #                 else:
    #                     if self.maxLength < i*15:
    #                         self.maxLength = i*15
    #                     i = 1
    #         if self.maxLength <= i*15:
    #             self.maxLength = i*15

class AvailableTimes(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    stylist = models.ForeignKey(SalonStylist, on_delete=models.CASCADE)
    date = models.DateField()
    availables = models.TextField(null=True)
    maxLength = models.PositiveSmallIntegerField(null=True)

    class Meta:
        unique_together = ['salonAcc', 'stylist', 'date']
        ordering = ['date', 'pk']
    


    def get_opening_time(self):
        if SpecialOpenTime.objects.filter(salonAcc=self.salonAcc, date=self.date):
            return SpecialOpenTime.objects.filter(salonAcc=self.salonAcc, date=self.date).first()
        if not ClosedDay.objects.filter(salonAcc=self.salonAcc, date=self.date):
            opening_time = OpenTimes.objects.filter(day=self.date.weekday(), salonAcc=self.salonAcc).first()
            logger.debug('Open day')
            return opening_time
        else:
            logger.debug('Close day')
            return OpenTimes.objects.filter(day=self.date.weekday(), salonAcc=self.salonAcc).first()

    def unavailable_times(self):
        unavailable_times = []
        stylist = self.stylist
        openingTime = self.get_opening_time()
        opentime = datetime.combine(self.date, openingTime.openTime)
        closetime = datetime.combine(self.date, openingTime.closeTime)
        exiting_appntms = Appointment.objects.filter(salonAcc=self.salonAcc, stylist=self.stylist, dateTime__range=(opentime, closetime))
        for exiting_appmt in exiting_appntms:
            check_slot = exiting_appmt.dateTime

            app_length = exiting_appmt.service.length
            for extra in exiting_appmt.extras.all():
                app_length += extra.length
            while check_slot < exiting_appmt.dateTime + timedelta(minutes=app_length):
                
                unavailable_times.append(check_slot.strftime('%Y-%m-%d %H:%M:%S'))
                check_slot += timedelta(minutes=15)
        logger.debug(f'unavailable times {unavailable_times}')
        return unavailable_times
    def create_availables_times(self):
        openingTime = self.get_opening_time()
        if openingTime.openTime and openingTime.closeTime:
            logger.debug(openingTime)
            slot_str = '{} {}'.format(self.date.strftime('%Y-%m-%d'), openingTime.openTime.strftime('%H:%M:%S'))
            slot = datetime.strptime(slot_str, '%Y-%m-%d %H:%M:%S')
            availables = []
            while slot.time() < openingTime.closeTime:
                availables.append(slot.strftime('%Y-%m-%d %H:%M:%S'))
                slot += timedelta(minutes=15)
            for slot in self.unavailable_times():
                print(slot, type(slot))
                try:
                    availables.remove(slot)
                except Exception as e:
                    logger.exception(e)
            self.availables = ','.join(availables)
            self.get_max_length()



        

    def get_max_length(self, *args, **kwargs):
        i = 0
        self.maxLength = 0
        # print('string availables', self.availables)
        
        if self.availables:
            availables = self.availables.split(',') 
            # print('available length', len(availables))

            if len(availables) >= 1:

                self.maxLength = 15
                        
            # print('check max length', availables)
                check_slot = datetime.strptime(availables[0], '%Y-%m-%d %H:%M:%S')
                for k in range(0, len(availables)):
                    if k == 0:
                        i +=1
                    else:
                        slot_time = datetime.strptime(availables[k], '%Y-%m-%d %H:%M:%S')
                        check_slot = datetime.strptime(availables[k-1], '%Y-%m-%d %H:%M:%S')            
                        if slot_time - check_slot <= timedelta(minutes=15):
                            i += 1
                        else:
                            if self.maxLength < i*15:
                                self.maxLength = i*15
                            i = 1
                if self.maxLength <= i*15:
                    self.maxLength = i*15





class AvailableChairTimes(models.Model):

    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    pedChair = models.ForeignKey(PedicureChairs, on_delete=models.CASCADE)
    date = models.DateField()
    ped_availables = models.TextField(null=True, blank=True)
    ped_maxLength = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['salonAcc', 'pedChair', 'date']
        ordering = ['date', 'pk']

    # def __init__(self, *args, **kwargs):
 
    #     super().__init__(*args, **kwargs)
    #     self.create_availables_times()

    # def save(self, *args, **kwargs):
    #     self.create_availables_times()
    #     super().save(*args, **kwargs)

    def get_opening_time(self):
        logger.debug(self.date)
        if SpecialOpenTime.objects.filter(salonAcc=self.salonAcc, date=self.date):
            return SpecialOpenTime.objects.filter(salonAcc=self.salonAcc, date=self.date).first()
        if not ClosedDay.objects.filter(salonAcc=self.salonAcc, date=self.date):
            opening_time = OpenTimes.objects.filter(day=self.date.weekday(), salonAcc=self.salonAcc).first()
            logger.debug('Open day')
            return opening_time
        else:
            logger.debug('Close day')

    
    def create_availables_times(self):

        openingTime = self.get_opening_time()
        if openingTime.openTime and openingTime.closeTime:
            logger.debug(openingTime)
            slot_str = '{} {}'.format(self.date.strftime('%Y-%m-%d'), openingTime.openTime.strftime('%H:%M:%S'))
            slot = datetime.strptime(slot_str, '%Y-%m-%d %H:%M:%S')
            ped_availables = []
            while slot.time() < openingTime.closeTime:
                ped_availables.append(slot.strftime('%Y-%m-%d %H:%M:%S'))
                slot += timedelta(minutes=15)
            self.ped_availables = ','.join(ped_availables)
            self.get_max_length()

    def get_max_length(self, *args, **kwargs):
        ped_availables = self.ped_availables.split(',')
        check_slot = datetime.strptime(ped_availables[0], '%Y-%m-%d %H:%M:%S')
        i = 0
        self.ped_maxLength = 0
        if len(ped_availables) > 0:
            self.ped_maxLength = 15
            for k in range(0, len(ped_availables)):
                if k == 0:
                    i +=1
                else:
                    slot_time = datetime.strptime(ped_availables[k], '%Y-%m-%d %H:%M:%S')
                    check_slot = datetime.strptime(ped_availables[k-1], '%Y-%m-%d %H:%M:%S')           
                    if slot_time - check_slot <= timedelta(minutes=15):
                        i += 1
                    else:
                        if self.ped_maxLength < i*15:
                            self.ped_maxLength = i*15
                        i = 1
            if self.ped_maxLength <= i*15:
                self.ped_maxLength = i*15


class NotTurnedUp(models.Model):
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    dateTime = models.DateTimeField()
    service = models.ForeignKey(ServiceBlock, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Not tunred up"
        verbose_name_plural = "Not tunred ups"

    def __str__(self):
        return f'{self.customer} {self.dateTime} {self.service}'

    # def get_absolute_url(self):
    #     return reverse("_detail", kwargs={"pk": self.pk})
