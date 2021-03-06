from customers.models import Appointment, AvailableTimes, SalonStylist, ClosedDay, OpenTimes, AvailableChairTimes, PedicureChairs
from datetime import datetime, timedelta
from users.models import SalonAccount
from django.shortcuts import get_object_or_404
import random, string

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

class TempAppointment(Appointment):

    def get_available_days(self, *args, **kwargs):
        # print('loop')
        stylists = SalonStylist.objects.filter(salonAcc=self.salonAcc)
        available_days_list = []
        appointment_length = self.service.length
        for extra in self.temp_extras:
            appointment_length += extra.length
        for stylist in stylists:
            for i in range(0, self.salonAcc.futureAppointment):
                check_day = datetime.today() + timedelta(days=i)
                opening_time = OpenTimes.objects.filter(salonAcc=self.salonAcc, day=check_day.weekday()).first()
                if not ClosedDay.objects.filter(salonAcc=self.salonAcc, date=check_day).exists():
                    if opening_time.openTime and opening_time.closeTime:
                        # print(check_day)
                        available_days_list.append(check_day.strftime('%Y-%m-%d'))
        
        if hasattr(self, 'stylist'):
            sty_available_days = AvailableTimes.objects.filter(salonAcc=self.salonAcc, stylist=self.stylist, date__gte=check_day)
            for day in sty_available_days:
                if day.maxLength < appointment_length:
                    available_days_list.remove(day.date.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            available_days = AvailableTimes.objects.filter(salonAcc=self.salonAcc, date__gte=check_day)
            for day in available_days:
                if day.maxLength < appointment_length:
                    available_day = AvailableTimes.objects.filter(salonAcc=self.salonAcc, date=day.date)
                    if len(available_day) < len(stylists):
                        for stylist in stylists:
                            try:
                                avbl = AvailableTimes.objects.create(salonAcc=self.salonAcc, stylist=stylist, date=day.date)
                                avbl.create_availables_times()
                                avbl.get_max_length()
                            except:
                                pass
                    else:
                        if not available_day.filter(maxLength__gte=appointment_length):
                            available_days_list.remove(day.date.strftime('%Y-%m-%d %H:%M:%S'))
        if not ClosedDay.objects.filter(salonAcc=self.salonAcc, date=datetime.today()).exists():
            today_opening_time = OpenTimes.objects.filter(salonAcc=self.salonAcc, day=datetime.today().weekday()).first()
            if today_opening_time.openTime and today_opening_time.closeTime:
            # print(ClosedDay.objects.filter(salonAcc=self.salonAcc, date=datetime.today()))
                if self.get_available_times(date=datetime.today()) != []:
                    available_days_list.remove(datetime.now().strftime('%Y-%m-%d'))
            # print('add',datetime.now().strftime('%Y-%m-%d'))
        # print(available_days_list)
        return available_days_list



    def get_available_times(self, *args, **kwargs):
        current_slots = []
        # try:
        if 'current_appointment' in kwargs:
            current_appointment = kwargs['current_appointment']
            
            current_slots.append(current_appointment.stylist)
            current_app_length = current_appointment.service.length
            for extra in current_appointment.extras.all():
                current_app_length += extra.length
            check_time = current_appointment.dateTime
            while check_time < current_appointment.dateTime + timedelta(minutes=current_app_length):
                current_slots.append(check_time.strftime('%Y-%m-%d %H:%M:%S'))
                check_time += timedelta(minutes=15)
            # logger.debug(f'Current appoitment slots {current_slots}')

        appmt_length = self.service.length
        for extra in self.temp_extras:
            appmt_length += extra.length
        appmt_slots_required = appmt_length/15
        date = kwargs['date']            
        if hasattr(self, 'stylist'):
            day_avaiables = AvailableTimes.objects.filter(salonAcc=self.salonAcc, date=date, stylist=self.stylist)
        else:
            day_avaiables = AvailableTimes.objects.filter(salonAcc=self.salonAcc, date=date)
        
        stylists = SalonStylist.objects.filter(salonAcc=self.salonAcc)
        if len(day_avaiables) <len(stylists):
            for stylist in stylists:
                if not AvailableTimes.objects.filter(salonAcc=self.salonAcc, stylist=stylist, date=date):
                    avbl = AvailableTimes(salonAcc=self.salonAcc, stylist=stylist, date=date)
                    avbl.save()
                    avbl.create_availables_times()
                    avbl.get_max_length()
                    avbl.save()
        if hasattr(self, 'stylist'):
            day_avaiables = AvailableTimes.objects.filter(salonAcc=self.salonAcc, date=date, stylist=self.stylist)
        else:
            day_avaiables = AvailableTimes.objects.filter(salonAcc=self.salonAcc, date=date)
        # logger.debug('available day objects {}'.format(day_avaiables))
        checked_available_times = []
        
        for day in day_avaiables:
            print(day.date)
            

            available_slots = day.availables.split(',')
            if day.date == datetime.now().date():
                temp = []
                if not day.availables:
                    available_slots = []
                else:
                    try:
                        for slot in available_slots:
                            if datetime.strptime(slot, '%Y-%m-%d %H:%M:%S') > datetime.now():
                                temp.append(slot)
                        available_slots = temp
                    except:
                        pass
            if current_slots:
                if day.stylist == current_slots[0]:
                    for i in range(1, len(current_slots)):
                        available_slots.append(current_slots[i])
            available_slots.sort()
            # logger.debug('checking day object {} slots {}'.format(day, available_slots))
            
            try:
                for i in range(len(available_slots)-1, -1, -1):
                    # print(i)
                    
                    if i == len(available_slots)-1:
                        
                        k = 1
                        # logger.debug('k {} lots required {}'.format(k, appmt_slots_required))
                    elif datetime.strptime(available_slots[i+1], '%Y-%m-%d %H:%M:%S')  - datetime.strptime(available_slots[i], '%Y-%m-%d %H:%M:%S') <= timedelta(minutes=15):
                        k += 1
                        # logger.debug(datetime.strptime(available_slots[i+1], '%Y-%m-%d %H:%M:%S') - datetime.strptime(available_slots[i], '%Y-%m-%d %H:%M:%S'))
                        
                        # logger.debug('k {} lots required {}'.format(k, appmt_slots_required))

                        if k >= int(appmt_slots_required):
                            # logger.debug(f'{available_slots[i+1]},  {available_slots[i]} k {k} checked_available_times {checked_available_times}')
                            checked_available_times.append(available_slots[i])

                    else:
                        # logger.debug(datetime.strptime(available_slots[i+1], '%Y-%m-%d %H:%M:%S')  - datetime.strptime(available_slots[i], '%Y-%m-%d %H:%M:%S'))
                        k = 1
            except:
                pass
            # if current_slots:
            #     if day.stylist == current_slots[0]:
            #         for i in range(1, len(current_slots)):
            #             checked_available_times.append(current_slots[i])

        return checked_available_times

        # except Exception as e:
        #     print(e)
        #     logger.debug('get_available_times exception {}'.format(e))

    def save_appointment(self, *args, **kwargs):

        letters = string.ascii_letters
        cancelID = ''.join(random.choice(letters) for i in range(10))
        while Appointment.objects.filter(cancelID=cancelID):
            cancelID = ''.join(random.choice(letters) for i in range(10))
        length = self.service.length
        for extra in self.temp_extras:
            length += extra.length
        logger.debug(self.get_available_times(date=self.dateTime.date()))
        if not hasattr(self, 'stylist'):
            availables = AvailableTimes.objects.filter(salonAcc=self.salonAcc, date=self.dateTime.date(), maxLength__gte=length)
            stylists = []
            for available in availables:
                available_list = available.availables.split(',')
                self.stylist = available.stylist
           
                # logger.debug('{} {}'.format(self.dateTime.strftime('%Y-%m-%d %H:%M:%S'), self.get_available_times(date=self.dateTime.date())))

                if self.dateTime.strftime('%Y-%m-%d %H:%M:%S') in self.get_available_times(date=self.dateTime.date()):
                    # print(self.stylist)
                    index = available_list.index(self.dateTime.strftime('%Y-%m-%d %H:%M:%S'))
                    # logger.debug(f'appointment stylist {available.stylist} {index}')
                    if index != 0:
                        k = 0
                        while index -1 >= 0:
                            try:
                                if datetime.strptime(available_list[index], '%Y-%m-%d %H:%M:%S') - datetime.strptime(available_list[index-1], '%Y-%m-%d %H:%M:%S') <= timedelta(minutes=15):
                                    k += 1
                                else:
                                    index = 0
                            except:
                                pass
                            index -= 1
                        m = k%4
                        n = k // 4
                        stylists.append([m,n,k,available.stylist])
                        logger.debug(f'appointment stylists {stylists}')
                    else:
                        stylists.append([0,0,0,available.stylist])


            if stylists:    
                def takefirst(elem):
                    return elem[0]
                stylists.sort(key=takefirst)
                if stylists[0][0] == 0:
                    self.stylist = stylists[0][3]
                else:
                    self.stylist = stylists[-1][3]
        # print('here')
        # logger.debug(self.get_available_times(date=self.dateTime.date()))
        if 'current_appointment' in kwargs:
            current_appointment = kwargs['current_appointment']
            available_times = self.get_available_times(date=self.dateTime.date(), current_appointment=current_appointment)
            current_appointment.delete()
        else:
            available_times = self.get_available_times(date=self.dateTime.date())
        if self.dateTime.strftime('%Y-%m-%d %H:%M:%S') in available_times:

            appointment = Appointment.objects.create(salonAcc=self.salonAcc,
                                        notice=self.notice,
                                        customer=self.customer,
                                        stylist=self.stylist,
                                        service=self.service,                                 
                                        dateTime=self.dateTime,                                
                                        cancelID=cancelID,
                                        )
            appointment.save()
            for extra in self.temp_extras:
                appointment.extras.add(extra)
            appointment.save()
        else:
            appointment = None

        return appointment







        
    def get_ped_available_times(self, *args, **kwargs):
        # print('here')
        ped_current_slots = []
        # try:
        if 'current_appointment' in kwargs:
            current_appointment = kwargs['current_appointment']
            
            ped_current_slots.append(current_appointment.pedChair)
            ped_current_app_length = current_appointment.service.pedicure_chair_length
            check_time = current_appointment.dateTime
            if ped_current_app_length:
                while check_time < current_appointment.dateTime + timedelta(minutes=ped_current_app_length):
                    ped_current_slots.append(check_time.strftime('%Y-%m-%d %H:%M:%S'))
                    check_time += timedelta(minutes=15)
                logger.debug(f'Current ped appoitment slots {ped_current_slots}')

        ped_appmt_length = self.service.pedicure_chair_length

        ped_appmt_slots_required = ped_appmt_length/15
        date = kwargs['date']            

        ped_day_avaiables = AvailableChairTimes.objects.filter(salonAcc=self.salonAcc, date=date)
        logger.debug(f'ped_day_avaiables {ped_day_avaiables}')
        
        chairs = PedicureChairs.objects.filter(salonAcc=self.salonAcc)
        logger.debug(f'chairs {chairs}')
        if len(ped_day_avaiables) <len(chairs):
            for pedChair in chairs:
                if not AvailableChairTimes.objects.filter(salonAcc=self.salonAcc, pedChair=pedChair, date=date):
                    avbl = AvailableChairTimes(salonAcc=self.salonAcc, pedChair=pedChair, date=date)
                    avbl.create_availables_times()
                    avbl.get_max_length()
                    avbl.save()

        ped_day_avaiables = AvailableChairTimes.objects.filter(salonAcc=self.salonAcc, date=date)
        # logger.debug('available day objects {}'.format(day_avaiables))
        ped_checked_available_times = []
        for day in ped_day_avaiables:
            logger.debug(f' day {day}')
            # Get available slots 
            available_slots = day.ped_availables.split(',')
            if ped_current_slots:
                logger.debug(f'{day.pedChair} {ped_current_slots[0]}')
                if day.pedChair == ped_current_slots[0] and day.date == current_appointment.dateTime.date():
                    # logger.debug(f' day.pedChair {day.pedChair} ped_current_slots[0] {ped_current_slots[0]}')
                    for i in range(1, len(ped_current_slots)):
                        # add current appointment slots to available slots
                        available_slots.append(ped_current_slots[i])
            available_slots.sort()
            logger.debug('checking day object {} slots {}'.format(day, available_slots))
            
      
            for i in range(len(available_slots)-1, -1, -1):
                # print(i)
                
                if i == len(available_slots)-1:
                    
                    k = 1
                    # logger.debug('k {} lots required {}'.format(k, ped_appmt_slots_required))
                elif datetime.strptime(available_slots[i+1], '%Y-%m-%d %H:%M:%S')  - datetime.strptime(available_slots[i], '%Y-%m-%d %H:%M:%S') <= timedelta(minutes=15):
                    k += 1
                    # logger.debug(datetime.strptime(available_slots[i+1], '%Y-%m-%d %H:%M:%S')  - datetime.strptime(available_slots[i], '%Y-%m-%d %H:%M:%S'))
                    # logger.debug('k {} lots required {}'.format(k, ped_appmt_slots_required))

                    if k >= int(ped_appmt_slots_required):
                        ped_checked_available_times.append(available_slots[i])

                else:
                    # logger.debug(datetime.strptime(available_slots[i+1], '%Y-%m-%d %H:%M:%S')  - datetime.strptime(available_slots[i], '%Y-%m-%d %H:%M:%S'))
                    k = 1


        return ped_checked_available_times

    def get_ped_available_days(self, *args, **kwargs):
        pedChairs = PedicureChairs.objects.filter(salonAcc=self.salonAcc)
        ped_available_days_list = []
        ped_appointment_length = self.service.pedicure_chair_length
        for pedChair in pedChairs:
            for i in range(0, self.salonAcc.futureAppointment):
                check_day = datetime.today() + timedelta(days=i)
                opening_time = OpenTimes.objects.filter(salonAcc=self.salonAcc, day=check_day.weekday()).first()
                if not ClosedDay.objects.filter(salonAcc=self.salonAcc, date=check_day):
                    if opening_time.openTime and opening_time.closeTime:
                        ped_available_days_list.append(check_day.strftime('%Y-%m-%d'))

        ped_available_days = AvailableChairTimes.objects.filter(salonAcc=self.salonAcc, date__gte=check_day)
        logger.debug(f'available chair objects {ped_available_days}')
        for day in ped_available_days:
            if day.ped_maxLength < ped_appointment_length:
                ped_available_day = AvailableChairTimes.objects.filter(salonAcc=self.salonAcc, date=day.date)
                if len(ped_available_day) < len(pedChairs):
                    for pedChair in pedChairs:
                        try:
                            logger.debug('created chair available times')
                            avbl = AvailableChairTimes.objects.create(salonAcc=self.salonAcc, pedChair=pedChair, date=day.date)
                            # avbl.create_availables_times()
                            # avbl.get_max_length()
                        except Exception as e:
                            logger.debug(e)
                else:
                    if not ped_available_day.filter(maxLength__gte=appointment_length):
                        ped_available_days_list.remove(day.date.strftime('%Y-%m-%d %H:%M:%S'))

        return ped_available_days_list