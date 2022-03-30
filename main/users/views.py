from django.shortcuts import render
from rest_framework import status

# Create your views here.
from django.shortcuts import render, reverse
from customers.models import TemplateAppointment, GenaralOpenTime, SpecialOpenTime, WeeklyCloseDay ,StoreLocker, Customer, Appointment, SalonStylist, ClosedDay, ServiceBlock, ExtraServiceBlock
from datetime import time, timedelta, date, datetime
from django.views.generic import CreateView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.contrib import messages
import calendar, random, string
from django.contrib.auth.decorators import login_required, permission_required
from users.models import SalonAccount, CustomUser
# from customers.appointment import SalonStylist, ServiceBlock
import time as ostime
import threading
from users.decorators import manager_required
from users.serializers import SalonAccountSerializer, StylistSerializer, ServiceBlocksSerializer, ExtraServiceBlocksSerializer
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import generics
from pathlib import Path
import logging, os

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

# class CustomViewSet(viewsets.ModelViewSet):
    
#     model = None
#     def get_queryset(self):
#         """
#         This view should return a list of all the purchases for
#         the user as determined by the username portion of the URL.
#         """
#         salonAcc = self.request.user.salonAcc
#         return self.model.objects.filter(salonAcc=salonAcc)
    
 

#     def create(self, request, *args, **kwargs):
#         request.data._mutable = True
#         # request.data['salonAcc'] = request.user.salonAcc
#         logger.debug(request.user.salonAcc)
#         request.data['salonAcc'] = '{}{}/'.format(reverse('salonaccount-list'),request.user.salonAcc.pk)
#         logger.debug(request.data['salonAcc'])
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#     def destroy(self, request, *args, **kwargs):

#         instance = self.get_object()
#         if request.user.salonAcc == instance.salonAcc:
#             logger.debug(instance.salonAcc)
#             self.perform_destroy(instance)
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response(status=status.HTTP_403_FORBIDDEN)

#     def get_object(self):
#         """
#         Returns the object the view is displaying.

#         You may want to override this if you need to provide non-standard
#         queryset lookups.  Eg if objects are referenced using multiple
#         keyword arguments in the url conf.
#         """
#         queryset = self.filter_queryset(self.get_queryset())

#         # Perform the lookup filtering.
#         lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

#         assert lookup_url_kwarg in self.kwargs, (
#             'Expected view %s to be called with a URL keyword argument '
#             'named "%s". Fix your URL conf, or set the `.lookup_field` '
#             'attribute on the view correctly.' %
#             (self.__class__.__name__, lookup_url_kwarg)
#         )

#         filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
#         obj = get_object_or_404(queryset, **filter_kwargs)

#         # May raise a permission denied
#         self.check_object_permissions(self.request, obj)

#         return obj



# class ServiceBlocksViewSet(CustomViewSet):
#     model = ServiceBlock
#     serializer_class = ServiceBlocksSerializer
#     queryset = ServiceBlock.objects.all()
#     permission_classes = ( IsAuthenticated, )

# class StylistsViewSet(CustomViewSet):

#     model = SalonStylist
#     serializer_class = StylistSerializer
#     queryset = SalonStylist.objects.all()
#     permission_classes = ( IsAuthenticated, )

# class ExtraServiceBlocksViewSet(CustomViewSet):

#     model = ExtraServiceBlock
#     serializer_class = StylistSerializer
#     queryset = ExtraServiceBlock.objects.all()
#     permission_classes = ( IsAuthenticated, )



# class SalonAccountsViewSet(viewsets.ModelViewSet):
#     queryset = SalonAccount.objects.filter()
#     serializer_class = SalonAccountSerializer
#     permission_classes = ( IsAuthenticated, IsAdminUser)
#     def get(self, request, format=None):
#         """
#         Return a list of all users.
#         """
#         logger.debug('Salon Account {}'.format(request.user.salonAcc))
#         queryset = SalonAccount.objects.filter(salonAcc=request.user.salonAcc)
#         serializer = SalonAccountSerializer(queryset, many=True, context={'request': request})
#         logger.debug(serializer.data)
#         return Response(serializer.data)
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# def add_stylist(request):
#     if request.method == 'POST':
#         req = request.POST

#         rev = reverse('verify')
#         rev = '{}?id={}'.format(rev, appoinmentID)
#         return HttpResponseRedirect(rev)        


@login_required
def salon_account(request):
    if request.method == 'POST':
        req = request.POST

        rev = reverse('verify')
        rev = '{}?id={}'.format(rev, appoinmentID)
        return HttpResponseRedirect(rev)        

    else:
        reqst = request
        if reqst.user.salonAcc:
            salonAcc = reqst.user.salonAcc
        else:
            salonAcc = None
        logger.debug('Salon Account {}'.format(salonAcc))
        context = {
            'salonAcc':salonAcc,
            # 'stylists':stylists,
        }
        return render(request, 'users/salon_account_create_form.html', context)



def salon_admin(request):
    reqst = request
    salonAcc = SalonAccount.objects.filter(website=reqst.META['HTTP_HOST']).first()
    print(reqst.META['HTTP_HOST'])
    base_context = {
        'salon_name':salonAcc.salonName,

    }
    return render(request, 'users/user.html', base_context)
# def signup(request):
#         if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('home')
#     else:
#         form = UserCreationForm()
#     return render(request, 'signup.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        rev = reverse('appointments')
        return HttpResponseRedirect(rev)
    if request.method == 'POST':
        req = request.POST


        print(req['email'])
        print(req['password'])

    return render(request, 'users/login.html')

from django.contrib.auth import views as auth_views
from django.shortcuts import resolve_url

class CusLoginView(auth_views.LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        return resolve_url('appointments')


def privacy_policy(request):
 

    return render(request, 'users/privacy_policy.html')

def terms_conditions(request):

    return render(request, 'users/terms_conditions.html')


