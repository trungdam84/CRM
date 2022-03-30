from django.contrib import admin
from .models import ExcetionLogs

# Register your models here.
class ExcetionLogsAdmin(admin.ModelAdmin):

    list_display = [field.name for field in ExcetionLogs._meta.fields if field.name != "id"]

admin.site.register(ExcetionLogs, ExcetionLogsAdmin)