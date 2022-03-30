from django.contrib import admin
from .models import NotTurnedUp, AvailableChairTimes, AvailableTimes, OpenTimes, PedicureChairs, CallerID ,AppointmentStatus, TemplateAppointment, Appointment, Customer, StoreLocker, SalonStylist, ClosedDay, WeeklyCloseDay, ServiceBlock, ExtraServiceBlock, SpecialOpenTime, GenaralOpenTime
from .models import QueueSMS, CustomerSession, SalonEquipment
# class NotTurnedUpsAdmin(admin.ModelAdmin):
#     list_display = ('__all__')

# class CustomerSessionAdmin(admin.ModelAdmin):
#     list_display = ('__all__')

class OpenTimesAdmin(admin.ModelAdmin):
    list_display = ('__all__')

class AppointmentStatusAdmin(admin.ModelAdmin):
    list_display = ('salonAcc','status')

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('salonAcc','customer','dateTime')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'salonAcc','firstName','lastName','mobile','tel','address_1','address_2','town','postCode')

class StoreLockerAdmin(admin.ModelAdmin):

    list_display = ('salonAcc','customer','boxNumber','clean')

class SpecialOpenTimeAdmin(admin.ModelAdmin):
    list_display = ('salonAcc','date', 'openTime','closeTime')


class ExtraServiceBlockAdmin(admin.ModelAdmin):
    list_display = ('salonAcc','name', 'length')

class TemplateAppointmentAdmin(admin.ModelAdmin):
    list_display = ('createdTime', 'updatedTime', 'waitFrom', 'waitTo',)

class AvailableTimesAdmin(admin.ModelAdmin):
    list_display = ('date', 'salonAcc', 'stylist', 'maxLength',)

class AvailableChairTimesAdmin(admin.ModelAdmin):
    list_display = ('date', 'salonAcc', 'pedChair', 'ped_maxLength',)

class QueueSMSAdmin(admin.ModelAdmin):
    list_display = [field.name for field in QueueSMS._meta.fields if field.name != "id"]

class SalonEquipmentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SalonEquipment._meta.fields if field.name != "id"]

# Register your models here.

admin.site.register(AppointmentStatus, AppointmentStatusAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(StoreLocker, StoreLockerAdmin)
admin.site.register(SpecialOpenTime, SpecialOpenTimeAdmin)
admin.site.register(GenaralOpenTime)
admin.site.register(SalonStylist)
admin.site.register(ClosedDay)
admin.site.register(ServiceBlock)
admin.site.register(ExtraServiceBlock, ExtraServiceBlockAdmin)
admin.site.register(WeeklyCloseDay)
admin.site.register(TemplateAppointment, TemplateAppointmentAdmin)
admin.site.register(CallerID)
admin.site.register(PedicureChairs)
admin.site.register(QueueSMS, QueueSMSAdmin)
admin.site.register(OpenTimes)
admin.site.register(AvailableTimes, AvailableTimesAdmin)
admin.site.register(AvailableChairTimes, AvailableChairTimesAdmin)
admin.site.register(NotTurnedUp)
admin.site.register(CustomerSession)
admin.site.register(SalonEquipment, SalonEquipmentAdmin)




