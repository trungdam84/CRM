from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from .models import Appointment, AvailableTimes, OpenTimes, SalonStylist, ClosedDay, SalonStylist, AvailableChairTimes, PedicureChairs, SpecialOpenTime
from datetime import datetime, timedelta
from pathlib import Path
import logging, os

from django.conf import settings
from django.core.cache import cache
from customers.models import TemplateAppointment, ExtraServiceBlock, ServiceBlock
from django.shortcuts import render
from django.utils import timezone

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


logger.debug('Signals has imported')
# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()
@receiver(post_save, sender=Appointment)
def update_availables(sender, instance, created, **kwargs):
    print('here')
    AvailableTimes.objects.filter(stylist=instance.stylist, date=instance.dateTime.date()).first().create_availables_times()
    viewdate = instance.dateTime.date()
    salonAcc = instance.SalonAcc
    
    cache.delete(f'viewdate_{viewdate.strftime("%Y-%m-%d")}')
    closed = False
    stylists = SalonStylist.objects.filter(salonAcc=salonAcc)
    if SpecialOpenTime.objects.filter(date=viewdate, salonAcc=salonAcc):
        # print('specila openday')
        closed = False
        opening_time = SpecialOpenTime.objects.filter(date=viewdate, salonAcc=salonAcc).first()
    elif not ClosedDay.objects.filter(date=viewdate, salonAcc=salonAcc).first():
        # print(' not close day')
        opening_time = OpenTimes.objects.filter(salonAcc=salonAcc, day=viewdate.weekday()).first()
        closed = not (opening_time.openTime and opening_time.closeTime)



    rows = []
    openTime = datetime.strptime('{} {}'.format(viewdate.strftime('%Y-%m-%d'), opening_time.openTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
    closeTime = datetime.strptime('{} {}'.format(viewdate.strftime('%Y-%m-%d'), opening_time.closeTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
    slotTime = openTime
    waiting_list = TemplateAppointment.objects.filter(waitFrom__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0), waitFrom__lte=timezone.now().replace(hour=23, minute=59, second=59, microsecond=999), waitTo__gte=timezone.now())
    while slotTime <= closeTime:
            timeblock = []
            timeblock.append(slotTime.strftime('%H:%M:%S'))
            for stylist in stylists:
                timeblock.append('Available')
            appnts = Appointment.objects.filter(salonAcc=salonAcc, dateTime__range=(openTime, closeTime))
            # logger.debug(f'appointments query set {appnts}')
            for a, appnt in enumerate(appnts, start=1):
                appnt.length = appnt.service.length
                for extra in appnt.extras.all():
                    appnt.length += extra.length

                r = (a*60)%180                    
                b = (a*60)%180
                g = (a*60)%180
                for i, stylist in enumerate(stylists, start=1):
                    # logger.debug(f' app stylist {appnt.stylist}  checking stylist {stylist}')
                    if appnt.stylist == stylist:
                        # print('app datetime is naive :',appnt.dateTime.is_naive())
                        if (appnt.dateTime <= slotTime) and ((appnt.dateTime+ timedelta(minutes=appnt.length-1)) > slotTime ):
                            if appnt.service.pedicure_chair_length:
                                b = 0
                            for extra in appnt.extras.all():
                                if extra.length < 0:
                                    r = 255
                            appnt.r = r
                            appnt.b = b
                            appnt.g = g
                            appnt.locker = StoreLocker.objects.filter(salonAcc=salonAcc, customer=appnt.customer).first()
                            timeblock[i] = appnt
            rows.append(timeblock)
            slotTime += timedelta(minutes=15)
    waitting_list_dates = []
    # _date = timezone.now()
    for i in range(0, 7):
        _date = timezone.now() + timedelta(days=i)
        def openingTime(_date, salonAcc):
            if SpecialOpenTime.objects.filter(salonAcc=salonAcc, date=_date):
                return SpecialOpenTime.objects.filter(salonAcc=salonAcc, date=_date).first()
            if not ClosedDay.objects.filter(salonAcc=salonAcc, date=_date):
                return OpenTimes.objects.filter(day=_date.weekday(), salonAcc=salonAcc).first()
            else:
                logger.debug('Close day')
                return OpenTimes.objects.filter(day=_date.weekday(), salonAcc=salonAcc).first()
        openingTime = openingTime(_date, salonAcc)
        if openingTime.openTime and openingTime.closeTime:      

            waitting_list_dates.append(_date)
    extraservices = ExtraServiceBlock.objects.filter(salonAcc=salonAcc)
    serviceblocks = ServiceBlock.objects.filter(salonAcc=salonAcc)

    context = {

        'rows': rows,
        # 'weekday': weekday,
        'stylists': stylists,
        'viewdate':viewdate,
        'closed':closed,
        'salonAcc':salonAcc,
        'waiting_list':waiting_list,
        'waitting_list_dates':waitting_list_dates,
        'extraservices':extraservices.all(),
        'serviceblocks':serviceblocks,

    }
    response = render(instance.request, 'customers/appointments.html', context)
    cache.set(f'viewdate_{viewdate.strftime("%Y-%m-%d")}', response)
    print('set cache')


@receiver(post_save, sender=Appointment)
def update_availables(sender, instance, created, **kwargs):
    # print(kwargs)
    if created:
        available = AvailableTimes.objects.filter(salonAcc=instance.salonAcc,
                                                    stylist=instance.stylist,
                                                    date=instance.dateTime,
                                                    ).first()
        available_list = available.availables.split(',')
        checking_time = instance.dateTime
        length = instance.service.length

                                              
        while checking_time < instance.dateTime + timedelta(minutes=length):
            # logger.debug('checking_time {} instance.dateTime {}'.format(checking_time, instance.dateTime + timedelta(minutes=length)))
            # logger.debug('{} slot to remove {}'.format(available_list, checking_time.strftime('%Y-%m-%d %H:%M:%S')))
            try:
                available_list.remove(checking_time.strftime('%Y-%m-%d %H:%M:%S'))
                logger.debug('Remove {}'.format(checking_time.strftime('%Y-%m-%d %H:%M:%S')))
            except:
                pass
            checking_time += timedelta(minutes=15)

        # print(' done while')
        available.availables = ','.join(available_list)
        available.get_max_length()
        available.save()

        # update available time for pedicure chairs

        if instance.service.pedicure_chair_length:
            logger.debug(f'Appointment got ped service')
            ped_availables = AvailableChairTimes.objects.filter(salonAcc=instance.salonAcc, date=instance.dateTime.date(), ped_maxLength__gte=instance.service.pedicure_chair_length)
            pedChairs = []
            for ped_available in ped_availables:
                ped_available_list = ped_available.ped_availables.split(',')
                logger.debug(f'ped_available_list {ped_available_list} instance.dateTime {instance.dateTime}')
                # self.stylist = available.stylist

                if instance.dateTime.strftime('%Y-%m-%d %H:%M:%S') in ped_available_list:

                    index = ped_available_list.index(instance.dateTime.strftime('%Y-%m-%d %H:%M:%S'))
                    logger.debug(f'appointment ped chair {ped_available.pedChair} index {index}')
                    if index != 0:
                        k = 0
                        while index -1 >= 0:
                            try:
                                if datetime.strptime(ped_available_list[index], '%Y-%m-%d %H:%M:%S') - datetime.strptime(ped_available_list[index-1], '%Y-%m-%d %H:%M:%S') <= timedelta(minutes=15):
                                    k += 1
                                else:
                                    index = 0
                            except:
                                pass
                            index -= 1
                        m = k%3
                        n = k // 3
                        pedChairs.append([m,n,k,ped_available.pedChair])
                        logger.debug(f'appointment Ped chairs {pedChairs}')
                    else:
                        chair = ped_available.pedChair
                        break


            if pedChairs:    
                def takefirst(elem):
                    return elem[0]
                pedChairs.sort(key=takefirst)
                if pedChairs[0][0] == 0:
                    chair = pedChairs[0][3]
                else:
                    chair = pedChairs[-1][3]
            logger.debug(chair)
            ped_chair_avail_day = AvailableChairTimes.objects.filter(salonAcc=instance.salonAcc, date=instance.dateTime.date(), pedChair=chair).first()
            ped_avail_times_list = ped_chair_avail_day.ped_availables.split(',')
            check_slot = instance.dateTime
            end_time = instance.dateTime + timedelta(minutes=instance.service.pedicure_chair_length)
            # logger.debug(f'check_slot{check_slot} end appointment time {end_time}')
            while check_slot < end_time:
                # try:
                ped_avail_times_list.remove(check_slot.strftime('%Y-%m-%d %H:%M:%S'))
                # except:
                #     pass
                # print(check_slot)
                check_slot += timedelta(minutes=15)
            # print(ped_chair_avail_day.ped_availables)
            ped_chair_avail_day.ped_availables = ','.join(ped_avail_times_list)
            ped_chair_avail_day.get_max_length()
            ped_chair_avail_day.save()
            instance.pedChair = chair
            instance.save()
    else:        
        available = AvailableTimes.objects.filter(salonAcc=instance.salonAcc,
                                                    stylist=instance.stylist,
                                                    date=instance.dateTime,
                                                    ).first()
        available_list = available.availables.split(',')
        checking_time = instance.dateTime
        length = instance.service.length
        for extra in instance.extras.all():
            length += extra.length
        # print('Appointment length {}'.format(instance))

                                              
        while checking_time < instance.dateTime + timedelta(minutes=length):
            # logger.debug('checking_time {} instance.dateTime {}'.format(checking_time, instance.dateTime + timedelta(minutes=length)))
            # logger.debug('{} slot to remove {}'.format(available_list, checking_time.strftime('%Y-%m-%d %H:%M:%S')))
            try:
                available_list.remove(checking_time.strftime('%Y-%m-%d %H:%M:%S'))
                logger.debug('Remove {}'.format(checking_time.strftime('%Y-%m-%d %H:%M:%S')))
            except:
                pass
            checking_time += timedelta(minutes=15)

        print(' done while')
        available.availables = ','.join(available_list)
        available.get_max_length()
        available.save()



@receiver(post_delete, sender=Appointment)
def deleted(sender, instance, **kwargs):
    print('deleted')
    # available = AvailableTimes.objects.filter(salonAcc=instance.salonAcc,
    #                                             stylist=instance.stylist,
    #                                             date=instance.dateTime,
    #                                             ).first()
    try:
        available = AvailableTimes.objects.filter(stylist=instance.stylist, date=instance.dateTime.date()).first()
        available.create_availables_times()
        available.get_max_length()
        available.save()
        # available_list = available.availables.split(',')
        # checking_time = instance.dateTime
        # length = instance.service.length
        # for extra in instance.extras.all():
        #     length += extra.length
                                                
        # while checking_time < instance.dateTime + timedelta(minutes=length):
        #     # logger.debug('checking_time {} instance.dateTime {}'.format(checking_time, instance.dateTime + timedelta(minutes=length)))
        #     # logger.debug('{} slot to append {}'.format(available_list, checking_time.strftime('%Y-%m-%d %H:%M:%S')))
     
        #     if checking_time.strftime('%Y-%m-%d %H:%M:%S') not in available_list:
        #         available_list.append(checking_time.strftime('%Y-%m-%d %H:%M:%S'))


        #     checking_time += timedelta(minutes=15)

        # available_list.sort()
        # available.availables = ','.join(available_list)
        # available.get_max_length()
        # available.save()
    except Exception as e:
        logger.exception(e)


    # if instance.pedChair:
    #     ped_chair_avail_day = AvailableChairTimes.objects.filter(salonAcc=instance.salonAcc, date=instance.dateTime.date(), pedChair=instance.pedChair).first()
    #     try:
    #         ped_available_list = ped_chair_avail_day.ped_availables.split(',')
    #         checking_time = instance.dateTime
    
                                                    
    #         while checking_time < instance.dateTime + timedelta(minutes=instance.service.pedicure_chair_length):
    #             # logger.debug('checking_time {} instance.dateTime {}'.format(checking_time, instance.dateTime + timedelta(minutes=length)))
    #             # logger.debug('{} slot to append {}'.format(available_list, checking_time.strftime('%Y-%m-%d %H:%M:%S')))
    #             try:
    #                 ped_available_list.append(checking_time.strftime('%Y-%m-%d %H:%M:%S'))
    #             except:
    #                 pass
    #             checking_time += timedelta(minutes=15)
    #         ped_available_list.sort()
    #         ped_chair_avail_day.ped_availables = ','.join(ped_available_list)
    #         ped_chair_avail_day.get_max_length()
    #         ped_chair_avail_day.save()
    #     except Exception as e:
    #         logger.exception(e)







# @receiver(pre_save, sender=AvailableTimes)
# def create_other_fields(sender, instance, **kwargs):
#     print(kwargs)
#     instance.get_max_length()

@receiver(post_save, sender=AvailableChairTimes)
def create_other_fields(sender, instance, created, **kwargs):
    if created:
        instance.create_availables_times()

# @receiver(pre_save, sender=AvailableChairTimes)
# def create_other_fields(sender, instance, **kwargs):
#     # print(kwargs)
#     if kwargs['update_fields']:
#         instance.get_max_length()
#         logger.debug(f'AvailableChairTimes max length {instance.ped_maxLength}')


@receiver(post_save, sender=OpenTimes)
def change_open_times(sender, instance, **kwargs):
    print('change open times')
    day = instance.day
    salonAcc = instance.salonAcc
    available_times = AvailableTimes.objects.filter(salonAcc=salonAcc, date__gte=datetime.now())
    for available in available_times:
        if available.date.weekday() == day:
            if instance.openTime and instance.closeTime:
                open_time = datetime.strptime('{} {}'.format(available.date.strftime('%Y-%m-%d'), instance.openTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
                close_time = datetime.strptime('{} {}'.format(available.date.strftime('%Y-%m-%d'), instance.closeTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
                available.availables = ''
                # available.save()
                available.create_availables_times()
                available.save()
                appmts = Appointment.objects.filter(salonAcc=salonAcc, stylist=available.stylist, dateTime__range=(open_time, close_time))
                for appmt in appmts:
                    check_slot = appmt.dateTime
                    avail_list = available.availables.split(',')
                    app_length = appmt.service.length
                    for extra in appmt.extras.all():
                        app_length += extra.length
                    while check_slot < appmt.dateTime + timedelta(minutes=app_length):
                        
                        avail_list.remove(check_slot.strftime('%Y-%m-%d %H:%M:%S'))
                        check_slot += timedelta(minutes=15)
                    available.availables = ','.join(avail_list)

                available.get_max_length(save=True)
    ped_available_times = AvailableChairTimes.objects.filter(salonAcc=salonAcc, date__gte=datetime.now())
    for ped_available in ped_available_times:
        if ped_available.date.weekday() == day:
            if instance.openTime and instance.closeTime:
                open_time = datetime.strptime('{} {}'.format(ped_available.date.strftime('%Y-%m-%d'), instance.openTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
                close_time = datetime.strptime('{} {}'.format(ped_available.strftime('%Y-%m-%d'), instance.closeTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
                ped_available.availables = ''
                # ped_available.save()
                ped_available.create_availables_times()
                ped_available.save()
                appmts = Appointment.objects.filter(salonAcc=salonAcc, stylist=available.stylist, dateTime__range=(open_time, close_time))
                for appmt in appmts:
                    if appmt.service.pedicure_chair_length:
                        check_slot = appmt.dateTime
                        ped_avail_list = available.ped_availables.split(',')
                        while check_slot < appmt.dateTime + timedelta(minutes=appmt.service.pedicure_chair_length):
                            ped_avail_list.remove(check_slot.strftime('%Y-%m-%d %H:%M:%S'))
                            check_slot += timedelta(minutes=15)
                        available.ped_availables = ','.join(ped_avail_list)
                available.get_max_length(save=True)

@receiver(post_delete, sender=SpecialOpenTime)
def delete_special_open_time(sender, instance, **kwargs):
    day = instance.date.weekday()
    day_open_time = OpenTimes.objects.filter(salonAcc=instance.salonAcc, day=day).first()
    day_open_time.save()

@receiver(post_save, sender=SpecialOpenTime)
def change_special_open_time(sender, instance, **kwargs):
    date = instance.date
    available_times = AvailableTimes.objects.filter(salonAcc=instance.salonAcc, date=date)
    for available in available_times:
        if instance.openTime and instance.closeTime:
            open_time = datetime.strptime('{} {}'.format(instance.date.strftime('%Y-%m-%d'), instance.openTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
            close_time = datetime.strptime('{} {}'.format(instance.date.strftime('%Y-%m-%d'), instance.closeTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
            available.availables = ''
            # available.save()
            available.create_availables_times()
            available.save()
            avail_list = available.availables.split(',')
            appmts = Appointment.objects.filter(salonAcc=instance.salonAcc, stylist=available.stylist, dateTime__range=(open_time, close_time))
            for appmt in appmts:
                check_slot = appmt.dateTime
                
                app_length = appmt.service.length
                for extra in appmt.extras.all():
                    app_length += extra.length
                while check_slot < appmt.dateTime + timedelta(minutes=app_length):
                    print('Remove', available.stylist, check_slot.strftime('%Y-%m-%d %H:%M:%S'))
                    avail_list.remove(check_slot.strftime('%Y-%m-%d %H:%M:%S'))
                    check_slot += timedelta(minutes=15)
            
            available.availables = ','.join(avail_list)

            available.save()
            print(available.availables)
            available.get_max_length(save=True)
            available.save()
    ped_available_times = AvailableChairTimes.objects.filter(salonAcc=instance.salonAcc, date__gte=datetime.now())
    for ped_available in ped_available_times:
        if instance.openTime and instance.closeTime:
            open_time = datetime.strptime('{} {}'.format(instance.date.strftime('%Y-%m-%d'), instance.openTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
            close_time = datetime.strptime('{} {}'.format(instance.date.strftime('%Y-%m-%d'), instance.closeTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
            ped_available.availables = ''
            # ped_available.save()
            ped_available.create_availables_times()
            ped_available.save()
            ped_avail_list = ped_available.ped_availables.split(',')
            try:
                appmts = Appointment.objects.filter(salonAcc=instance.salonAcc, stylist=available.stylist, dateTime__range=(open_time, close_time))
                for appmt in appmts:
                    if appmt.service.pedicure_chair_length:
                        check_slot = appmt.dateTime
                        while check_slot < appmt.dateTime + timedelta(minutes=appmt.service.pedicure_chair_length):
                            try:
                                ped_avail_list.remove(check_slot.strftime('%Y-%m-%d %H-%M-%S'))
                            except:
                                pass
                            check_slot += timedelta(minutes=15)
            except:
                pass
            ped_available.ped_availables = ','.join(ped_avail_list)
            ped_available.save()
            ped_available.get_max_length(save=True)
            ped_available.save()
    
    # for i in range(0, salonAcc.futureAppointment):
    #     checking_day = datetime.today()

    #     checking_day += timedelta(days=i)
    #     if checking_day.weekday() == day:
    #         # print(checking_day)
    #         # Delete all available objects for checking day
    #         AvailableTimes.objects.filter(salonAcc=salonAcc, date=checking_day).delete()
    #         # Create new available objects for checking day with new open times
    #         if instance.openTime and instance.closeTime:
    #             open_time = datetime.strptime('{} {}'.format(checking_day.strftime('%Y-%m-%d'), instance.openTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
    #             close_time = datetime.strptime('{} {}'.format(checking_day.strftime('%Y-%m-%d'), instance.closeTime.strftime('%H:%M:%S')), '%Y-%m-%d %H:%M:%S')
    #             for stylist in SalonStylist.objects.filter(salonAcc=salonAcc):
    #                 print('create available {} sytlist {}'.format(checking_day, stylist))
    #                 available = AvailableTimes.objects.create(salonAcc=salonAcc, date=checking_day, stylist=stylist)
    #                 available.create_availables_times()
    #                 appmts = Appointment.objects.filter(salonAcc=salonAcc, stylist=stylist, dateTime__range=(open_time, close_time))
    #                 for appmt in appmts:
    #                     check_slot = appmt.dateTime
    #                     avail_list = available.availables.split(',')
    #                     while check_slot < appmt.endTime:
                            
    #                         avail_list.remove(check_slot.strftime('%H-%M-%S'))
    #                         check_slot += timedelta(minutes=15)
    #                     available.availables = ','.join(avail_list)
    #                     if appmt.service.pedicure_chair_length:
    #                         check_slot = appmt.dateTime
    #                         ped_avail_list = available.ped_availables.split(',')
    #                         while check_slot < appmt.dateTime + timedelta(minutes=appmt.service.pedicure_chair_length):
    #                             ped_avail_list.remove(check_slot.strftime('%H-%M-%S'))
    #                             check_slot += timedelta(minutes=15)
    #                         available.ped_availables = ','.join(ped_avail_list)
    #                 available.get_max_length(save=True)

@receiver(post_save, sender=ClosedDay)
def add_close_day(sender, instance, created, **kwargs):
    if created:
        salonAcc = instance.salonAcc
        AvailableTimes.objects.filter(salonAcc=salonAcc, date=instance.date).delete()

@receiver(post_delete, sender=ClosedDay)
def delete_close_day(sender, instance, **kwargs):
    salonAcc = instance.salonAcc
    try:
        for stylist in SalonStylist.objects.filter(salonAcc=salonAcc):
            available = AvailableTimes.objects.create(salonAcc=salonAcc, date=instance.date, stylist=stylist)
            available.create_availables_times()
            available.get_max_length()
    except Exception as e:
        logger.exception(e)

# @receiver(post_save, sender=SalonStylist)
# def create_stylist(sender, instance, created, **kwargs):
#     if created:
#         salonAcc = instance.salonAcc
#         for i in range(0, salonAcc.futureAppointment):
#             checking_day = datetime.today()
#             checking_day += timedelta(days=i)
#             if not ClosedDay.objects.filter(salonAcc=salonAcc, date=checking_day).first():
#                 open_time = OpenTimes.objects.filter(salonAcc=salonAcc, day=checking_day.weekday()).first()
#                 if open_time.openTime and open_time.closeTime:
#                     available = AvailableTimes.objects.create(salonAcc=salonAcc, date=checking_day, stylist=instance)
#                     available.create_availables_times()
#                     available.get_max_length(save=True)

@receiver(post_delete, sender=SalonStylist)
def delete_stylist(sender, instance, **kwargs):
    salonAcc = instance.salonAcc
    AvailableTimes.objects.filter(salonAcc=salonAcc, stylist=instance).delete()

@receiver(post_delete, sender=PedicureChairs)
def delete_stylist(sender, instance, **kwargs):
    salonAcc = instance.salonAcc
    AvailableChairTimes.objects.filter(salonAcc=salonAcc, pedChair=instance).delete()


