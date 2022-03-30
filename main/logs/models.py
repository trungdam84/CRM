from django.db import models

# Create your models here.
class ExcetionLogs(models.Model):
    module = models.CharField(max_length=250, blank=True, null=True)
    dateTime = models.DateTimeField()
    exception = models.TextField()
    error_code = models.CharField(max_length=10)