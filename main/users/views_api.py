
from users.models import SalonAccount, CustomUser
from customers.models import *
from rest_framework import status
from django.shortcuts import reverse, Http404
from django.shortcuts import get_object_or_404


from users.serializers import ( OpenTimesSerializer,
                                AvailableTimesSerializer, 
                                StylistSerializer, 
                                GenaralOpenTimesSerializer, 
                                SalonAccountSerializer, 
                                ServiceBlocksSerializer, 
                                ExtraServiceBlocksSerializer, 
                                WeeklyCloseDaysSerializer, 
                                PedicureChairsSerializer,
                                CustomersSerializer,
                                QueueSMSSerializer )


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

class CustomViewSet(viewsets.ModelViewSet):
    
    model = None
    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        salonAcc = self.request.user.salonAcc
        return self.model.objects.filter(salonAcc=salonAcc)
    
 

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        # request.data['salonAcc'] = request.user.salonAcc
        logger.debug(request.data)
        request.data['salonAcc'] = '{}{}/'.format(reverse('salonaccount-list'),request.user.salonAcc.pk)
        logger.debug(request.data['salonAcc'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        if request.user.salonAcc == instance.salonAcc:
            logger.debug(instance.salonAcc)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

class CustomersViewSet(CustomViewSet):
    model = Customer
    serializer_class = CustomersSerializer
    queryset = Customer.objects.all()
    permission_classes = ( IsAuthenticated, )

    def update(self, request, *args, **kwargs):
        request.data._mutable = True
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        request.data['salonAcc'] = '{}{}/'.format(reverse('salonaccount-list'),request.user.salonAcc.pk)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

class OpenTimesViewSet(CustomViewSet):
    model = OpenTimes
    serializer_class = OpenTimesSerializer
    queryset = OpenTimes.objects.all()
    permission_classes = ( IsAuthenticated, )

class AvailableTimesViewSet(CustomViewSet):
    model = AvailableTimes
    serializer_class = AvailableTimesSerializer
    queryset = AvailableTimes.objects.all()
    permission_classes = ( IsAuthenticated, )

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)


        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
    def get_queryset(self):
        from django.db.models.query import QuerySet
        # from django.db.models import Model
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.

        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.

        You may want to override this if you need to provide different
        querysets depending on the incoming request.

        (Eg. return a list of items that is specific to the user)
        """
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )

        req = self.request.GET


        # logger.debug(req)
        filter_kwargs = req.dict()
        # logger.debug(filter_kwargs)
        if filter_kwargs:
            queryset = self.queryset.filter(**filter_kwargs)
        else:
            queryset = self.queryset
        salonAcc = self.request.user.salonAcc
        req = self.request.GET
        req_kwargs = req.dict()
        logger.debug(req_kwargs)
        if not queryset:

            if 'date' in req_kwargs and 'stylist' in req_kwargs:
                req_kwargs['stylist'] = SalonStylist.objects.get(salonAcc=salonAcc, pk=req_kwargs['stylist'])
                obj = AvailableTimes(salonAcc=salonAcc, **req_kwargs)
                obj.save()
                obj = AvailableTimes.objects.filter(salonAcc=salonAcc, **req_kwargs).first()
                obj.create_availables_times()
                obj.get_max_length()


                logger.debug(obj)
            if 'date' in req_kwargs:
                stylists = SalonStylist.objects.filter(salonAcc=salonAcc)
                if len(stylists) > len(queryset):
                    logger.debug('Create availables')
                    for stylist in stylists:
                        # try:
                        req_kwargs['stylist'] = stylist
                        obj = AvailableTimes(salonAcc=salonAcc, **req_kwargs)
                        obj.save()
                        obj = AvailableTimes.objects.filter(salonAcc=salonAcc, **req_kwargs).first()
                        obj.create_availables_times()
                        obj.get_max_length()

                        # except Exception as e:
                        #     logger.debug(e)
        else:
            if 'date' in req_kwargs:
                stylists = SalonStylist.objects.filter(salonAcc=salonAcc)
                if len(stylists) > len(queryset):
                    logger.debug('Create availables')
                    for stylist in stylists:
                        # try:
                        req_kwargs['stylist'] = stylist
                        obj = AvailableTimes(salonAcc=salonAcc, **req_kwargs)
                        obj.save()
                        obj = AvailableTimes.objects.filter(salonAcc=salonAcc, **req_kwargs).first()
                        obj.create_availables_times()
                        obj.get_max_length()


                        # except Exception as e:
                        #     logger.debug(e)
                
        queryset = self.model.objects.filter(salonAcc=salonAcc, **filter_kwargs)

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset


class GenaralOpenTimesViewSet(CustomViewSet):
    model = GenaralOpenTime
    serializer_class = GenaralOpenTimesSerializer
    queryset = GenaralOpenTime.objects.all()
    permission_classes = ( IsAuthenticated, )

class WeeklyCloseDaysViewSet(CustomViewSet):
    model = WeeklyCloseDay
    serializer_class = WeeklyCloseDaysSerializer
    queryset = WeeklyCloseDay.objects.all()
    permission_classes = ( IsAuthenticated, )

class PedicureChairsViewSet(CustomViewSet):
    model = PedicureChairs
    serializer_class = PedicureChairsSerializer
    queryset = PedicureChairs.objects.all()
    permission_classes = ( IsAuthenticated, )

class ServiceBlocksViewSet(CustomViewSet):
    model = ServiceBlock
    serializer_class = ServiceBlocksSerializer
    queryset = ServiceBlock.objects.all()
    permission_classes = ( IsAuthenticated, )

class StylistsViewSet(CustomViewSet):

    model = SalonStylist
    serializer_class = StylistSerializer
    queryset = SalonStylist.objects.all()
    permission_classes = ( IsAuthenticated, )

class ExtraServiceBlocksViewSet(CustomViewSet):

    model = ExtraServiceBlock
    serializer_class = ExtraServiceBlocksSerializer
    queryset = ExtraServiceBlock.objects.all()
    permission_classes = ( IsAuthenticated, )



class SalonAccountsViewSet(viewsets.ModelViewSet):
    queryset = SalonAccount.objects.filter()
    serializer_class = SalonAccountSerializer
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        logger.debug('Salon Account {}'.format(request.user.salonAcc))
        queryset = SalonAccount.objects.filter(salonAcc=request.user.salonAcc)
        serializer = SalonAccountSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):

        assert(not request.user.salonAcc), 'User already have salon Account.'
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        
        headers = self.get_success_headers(serializer.data)
        from django.urls import resolve

        salon_pk = headers['Location'].split('/')[-2]
        logger.debug('Salon pk {}'.format(salon_pk))
        salonAcc = SalonAccount.objects.get(pk=salon_pk)
        user = request.user
        user.salonAcc = salonAcc
        user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class QueueSMSViewSet(CustomViewSet):
    model = QueueSMS
    serializer_class = QueueSMSSerializer
    queryset = QueueSMS.objects.all()
    permission_classes = ( IsAuthenticated, IsAdminUser)

