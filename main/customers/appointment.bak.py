from customers.models import ServiceBlock, Customer, GenaralOpenTime, WeeklyCloseDay, ClosedDay, SpecialOpenTime, ExtraServiceBlock, Appointment, SalonStylist, TemplateAppointment
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

class TemplateAppointments():

    def __init__(self, appointment, extras):
        try:
            self.appointment = appointment
            self.salonAcc = appointment.salonAcc
            self.length = appointment.service.length
            self.extras = extras
            for extra in extras:
                self.length += extra.length
            if not appointment.dateTime:
                self.appointment.dateTime = datetime.now()
            logger.debug('TemplateAppointment initialize appointment {} extras {}'.format(self.appointment, self.extras))
        except Exception as e:
            logger.exception('TemplateAppointment initialize error {}'.format(e))    
    def __repr__(self):
        return 'TemplateAppointment {} {}'.format(self.appointment, self.extras)

    def check_closed(self):
        try:
            closed = False
            for day in WeeklyCloseDay.objects.filter(salonAcc=self.salonAcc):
                if self.appointment.dateTime.weekday() == day.day:
                    closed = True
            if ClosedDay.objects.filter(date=self.appointment.dateTime.date(), salonAcc=self.salonAcc):
                closed = True  
            if SpecialOpenTime.objects.filter(date=self.appointment.dateTime.date(), salonAcc=self.salonAcc):
                closed = False
            logger.debug('Check closed day {} closed {}'.format(self.appointment.dateTime, closed))
            return closed
        except Exception as e:
            logger.exception('TemplateAppointment check closed day error {}'.format(e))

    def get_opening_time(self):
        try:
            viewdate = self.appointment.dateTime.date().strftime('%Y-%m-%d')
            if not self.check_closed():               
                if SpecialOpenTime.objects.filter(date=viewdate, salonAcc=self.salonAcc):
                    dayOpenTime = SpecialOpenTime.objects.filter(date=viewdate, salonAcc=self.salonAcc).first()                    
                    optimestr = str(viewdate) + ' ' + str(dayOpenTime.openTime)
                    cltimestr = str(viewdate) + ' ' + str(dayOpenTime.closeTime)
                    optime = datetime.strptime(optimestr, '%Y-%m-%d %H:%M:%S')
                    cltime = datetime.strptime(cltimestr, '%Y-%m-%d %H:%M:%S')

                else:
                    
                    dayOpenTime = GenaralOpenTime.objects.filter(salonAcc=self.salonAcc).first()
                    optimestr = str(viewdate) + ' ' + str(dayOpenTime.openTime)
                    cltimestr = str(viewdate) + ' ' + str(dayOpenTime.closeTime)
                    optime = datetime.strptime(optimestr, '%Y-%m-%d %H:%M:%S')
                    cltime = datetime.strptime(cltimestr, '%Y-%m-%d %H:%M:%S')
                opening_time = {
                    'open':optime,
                    'closed':cltime
                }
                logger.debug('TemplateAppointment get_opening_time viewdate {} opening time {}'.format(viewdate, opening_time))
                return opening_time
            else:
                logger.error('TemplateAppointment get_opening_time return null ')
                return
        except Exception as e:
            logger.exception('TemplateAppointment get_opening_time error {}'.format(e))

    def get_ped_available_times(self, *args, **kwargs):
        try:
            if not self.check_closed():
                opening_time = self.get_opening_time()
                logger.debug('TemplateAppointment get_ped_available_times opening time {}'.format(opening_time))
                ped_avail_times = []
                if PedicureChairs.objects.filter(salonAcc=self.salonAcc):
                    chairs = PedicureChairs.objects.filter(salonAcc=self.salonAcc)
                    logger.debug('TemplateAppointment get_ped_available_times all salon ped chair {}'.format(chairs))
                else:
                    logger.debug('TemplateAppointment get_ped_available_times salon has no ped chair')
                    return []
                for chair in chairs:
                    avail_time = opening_time['open']
                    while avail_time < opening_time['closed']:
                        ped_avail_times.append(avail_time)
                        avail_time += timedelta(minutes=15)
                if ServiceBlock.objects.filter(pedicure_chair=True, salonAcc=self.salonAcc):
                    for ped_service in ServiceBlock.objects.filter(pedicure_chair_length__isnull=False, salonAcc=self.salonAcc):
                        if 'update_appointment' in kwargs:
                            update_appointment = kwargs['update_appointment']
                            exitting_appointments = Appointment.objects.filter(dateTime__range=(opening_time['open'], opening_time['closed']), salonAcc=self.salonAcc, service=ped_service).exclude(pk=update_appointment.pk).order_by('dateTime')
                        else:
                            exitting_appointments = Appointment.objects.filter(dateTime__range=(opening_time['open'], opening_time['closed']), salonAcc=self.salonAcc, service=ped_service).order_by('dateTime')
                        logger.debug('TemplateAppointment get_ped_available_times all exitting ped appointment {}'.format(exitting_appointments))
                        for exitting_appointment in exitting_appointments:
                            exitting_slot = exitting_appointment.dateTime
                            exitting_appointment_length = exitting_appointment.service.pedicure_chair_length
                            while exitting_slot < (exitting_appointment.dateTime + timedelta(minutes=exitting_appointment_length)):
                                ped_avail_times.remove(exitting_slot)
                                exitting_slot += timedelta(minutes=15)                    
                    ped_unavail_slot = []
                    for slot in ped_avail_times:
                        avail = True
                        w_slot = slot
                        while w_slot < (slot + timedelta(minutes=self.appointment.service.pedicure_chair_length)):
                            if w_slot not in ped_avail_times:
                                avail = False
                                break
                            w_slot += timedelta(minutes=15)
                        if not avail:
                            ped_unavail_slot.append(slot)
                    for unavail_slot in ped_unavail_slot:
                        ped_avail_times.remove(unavail_slot)
                logger.debug('TemplateAppointment get_ped_available_times all available ped slot {}'.format(ped_avail_times))
                return ped_avail_times
            else:
                logger.debug('TemplateAppointment get_ped_avail_time closed day return available time []')
                return []                
        except Exception as e:
            logger.exception('TemplateAppointment get_ped_avail_time error {}'.format(e))        

    def get_available_times(self, *args, **kwargs):
        try:
            if not self.check_closed():
                opening_time = self.get_opening_time()

                if opening_time['open'] >= datetime.now():
                    checktime = opening_time['open']
                elif opening_time['open'] <= datetime.now():
                    checktime = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H'), '%Y-%m-%d %H')
                logger.debug('TemplateAppointment get_available_times check time {}'.format(checktime))
                all_avail_slots = []
                for stylist in SalonStylist.objects.filter(salonAcc=self.salonAcc):
                    stylist_avail_slots = []
                    slot = checktime
                    while slot < opening_time['closed']:
                        if slot >= datetime.now():
                            stylist_avail_slots.append(slot)
                        slot += timedelta(minutes=15)
                    logger.debug('TemplateAppointment get_available_times stylist_avail_slots {} stylist {}'.format(stylist_avail_slots, stylist))
                    if 'update_appointment' in kwargs:
                        update_appointment = kwargs['update_appointment']
                        exitting_appointments = Appointment.objects.filter(dateTime__range=(opening_time['open'], opening_time['closed']), stylist=stylist, salonAcc=self.salonAcc).exclude(pk=update_appointment.pk).order_by('dateTime')
                    else:
                        exitting_appointments = Appointment.objects.filter(dateTime__range=(opening_time['open'], opening_time['closed']), stylist=stylist, salonAcc=self.salonAcc).order_by('dateTime')
                    logger.debug('TemplateAppointment get_available_times exitting_appointments {} stylist {}'.format(exitting_appointments, stylist))
                    for exitting_appointment in exitting_appointments:
                        exitting_slot = exitting_appointment.dateTime
                        exitting_appointment_length = exitting_appointment.service.length
                        for extra in exitting_appointment.extras.all():
                            exitting_appointment_length += extra.length
                        while exitting_slot < (exitting_appointment.dateTime + timedelta(minutes=exitting_appointment_length)):
                            try:
                                stylist_avail_slots.remove(exitting_slot)
                                exitting_slot += timedelta(minutes=15)
                            except Exception as e:
                                exitting_slot += timedelta(minutes=15)
                    logger.debug('TemplateAppointment get_available_times stylist_avail_slots after remove exitting appointment slots {} stylist {}'.format(stylist_avail_slots, stylist))
                    stylist_unavail_slots =[]
                    for slot in stylist_avail_slots:
                        avail = True
                        w_slot = slot
                        while w_slot < (slot + timedelta(minutes=self.length)):
                            if w_slot not in stylist_avail_slots:
                                avail = False
                                break
                            w_slot += timedelta(minutes=15)
                        if not avail:
                            stylist_unavail_slots.append(slot)
                    for unavail_slot in stylist_unavail_slots:
                        stylist_avail_slots.remove(unavail_slot)
                    logger.debug('TemplateAppointment get_available_times with checking appointment lenght {} stylist {}'.format(self.length, stylist))
                    all_avail_slots.append([stylist, stylist_avail_slots])
                avail_slots = []
                for stylist in all_avail_slots:
                    if hasattr(self.appointment, 'stylist'):
                        if stylist[0] == self.appointment.stylist:
                            avail_slots = stylist[1]
                            logger.debug('TemplateAppointment get_available_times avail_slots for appointment with choosen stilist {} stylist {}'.format(avail_slots, stylist))
                            break
                    else:
                        for slot in stylist[1]:
                            avail_slots.append(slot)
                
                avail_slots = list(dict.fromkeys(avail_slots))
                
                avail_slots.sort()
                logger.debug('TemplateAppointment get_available_times avail_slots for appointment with all stilist {}'.format(avail_slots))
                if self.appointment.service.pedicure_chair_length:
                    if 'update_appointment' in kwargs:
                        update_appointment = kwargs['update_appointment']
                        ped_avail_times = self.get_ped_available_times(update_appointment=update_appointment)
                    else:
                        ped_avail_times = self.get_ped_available_times()
                    unavail_ped_slot = []
                    for slot in avail_slots:
                        if slot not in ped_avail_times:
                            unavail_ped_slot.append(slot)
                    for slot in unavail_ped_slot:
                        avail_slots.remove(slot)
                    logger.debug('TemplateAppointment get_available_times avail_slots for appointment after check ped available {}'.format(avail_slots))
                return avail_slots
            else:
                logger.debug('TemplateAppointment get_avail_time closed day return available time []')
                return []   
        except Exception as e:
            logger.exception('TemplateAppointment get_avail_time error {}'.format(e))
            
    def get_available_dates(self, days=120):
        try:
            availableDates = []

            for i in range(days):
                viewdate = datetime.now()
                
                viewdate += timedelta(days=i)
                logger.debug('TemplateAppointment get_avail_dates viewdate {}'.format(viewdate))
                self.appointment.dateTime = viewdate
                if not self.check_closed():
                
                    self.appointment.dateTime = self.get_opening_time()['open']

                    if self.get_available_times():
                        availableDates.append(viewdate.date())
            logger.debug('TemplateAppointment get_avail_dates {}'.format(availableDates))
            return availableDates
        except Exception as e:
            logger.exception('TemplateAppointment get_avail_dates error {}'.format(e))

    def save(self):
        try:
            opening_time = self.get_opening_time()
            if hasattr(self.appointment, 'stylist'):
                if self.appointment.dateTime in self.get_available_times():
                    self.appointment.save()
                    for extra in self.extras:
                        self.appointment.extras.add(extra)
                    self.appointment.save()
                    res = {
                        'error':0,
                        'message':self.appointment
                    }
                    return res
                res = {
                    'error':1,
                    'message':'Can not save Appointment, not available time.'
                }
                logger.debug('TemplateAppointment save with stylist {}'.format(self.appointment.stylist))
                return res
            earlyappnt_lenght = timedelta(minutes=0)
            for stylist in SalonStylist.objects.filter(salonAcc=self.salonAcc):
                self.appointment.stylist = stylist
                if self.appointment.dateTime in self.get_available_times():
                    self.appointment.save()
                    for extra in self.extras:
                        self.appointment.extras.add(extra)
                    self.appointment.save()
                    break
            for stylist in SalonStylist.objects.filter(salonAcc=self.salonAcc):
                appntb4check = Appointment.objects.filter(dateTime__range=(opening_time['open'], self.appointment.dateTime), stylist=stylist, salonAcc=self.appointment.salonAcc).exclude(pk=self.appointment.pk).order_by('-dateTime').first()
                
                if appntb4check:
                    logger.debug('TemplateAppointment save method has early appointment {} stylist {}'.format(appntb4check, self.appointment.stylist))
                    extra_length = 0
                    for extra in appntb4check.extras.all():
                        extra_length += extra.length
                    if appntb4check.dateTime + timedelta(minutes=appntb4check.service.length + extra_length) == self.appointment.dateTime:
                        self.appointment.stylist = stylist
                        self.appointment.save()
                        res = {
                            'error':0,
                            'message':self.appointment
                        }
                        logger.debug('TemplateAppointment save has early appointment {} with no early gap stylist {}'.format(appntb4check, self.appointment.stylist))
                        return res

                    elif appntb4check.dateTime + timedelta(minutes=appntb4check.service.length + extra_length) < self.appointment.dateTime:
                        if self.appointment.dateTime - (appntb4check.dateTime + timedelta(minutes=appntb4check.service.length + extra_length)) > earlyappnt_lenght:
                            self.appointment.stylist = stylist
                            self.appointment.save()
                            earlyappnt_lenght = self.appointment.dateTime - (appntb4check.dateTime + timedelta(minutes=appntb4check.service.length + extra_length))
                            logger.debug('TemplateAppointment save has early appointment {} early gap {} stylist {}'.format(appntb4check, earlyappnt_lenght, self.appointment.stylist))
            
                else:
                    self.appointment.stylist = stylist
                    self.appointment.save()
                    res = {
                        'error':0,
                        'message':self.appointment
                    }
                    logger.debug('TemplateAppointment save has no early appointment {} stylist {}'.format(appntb4check, self.appointment.stylist))
                    return res
                            
            res = {
                'error':0,
                'message':self.appointment
            }
            logger.debug('TemplateAppointment save final save appointment {} early gap {} stylist {}'.format(appntb4check, earlyappnt_lenght, self.appointment.stylist))
            return res
        except Exception as e:
            logger.exception('TemplateAppointment save error {}'.format(e))

    