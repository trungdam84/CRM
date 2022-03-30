from django.shortcuts import render
from pathlib import Path
import logging, os
from .sms_module import SMS
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required

logs_path = os.path.join(Path(settings.BASE_DIR).parents[0], 'logs')

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler(os.path.join(logs_path, 'sms.log'))

file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
# Create your views here.


@login_required
def read_smss(request):
    if request.user:
        smss = SMS()
        smss.read_all_sms()
    return HttpResponse(smss)
@login_required
def send_ussd(request):
    if request.user:
        smss = SMS()
        res = smss.ussd('*100#')
    return HttpResponse(res)