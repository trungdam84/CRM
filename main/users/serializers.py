from users.models import SalonAccount
from customers.models import QueueSMS, SalonStylist, ServiceBlock, ExtraServiceBlock, GenaralOpenTime, WeeklyCloseDay, PedicureChairs, AvailableTimes, OpenTimes, Customer
from rest_framework import routers, serializers, viewsets

class QueueSMSSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = QueueSMS

        fields = '__all__'


class OpenTimesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = OpenTimes

        fields = '__all__'

class AvailableTimesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = AvailableTimes

        fields = '__all__'

class GenaralOpenTimesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = GenaralOpenTime

        fields = '__all__'

class WeeklyCloseDaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = WeeklyCloseDay

        fields = '__all__'

class PedicureChairsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = PedicureChairs

        fields = '__all__'

class SalonAccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = SalonAccount

        fields = '__all__'

class StylistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = SalonStylist

        fields = '__all__'

   

class ServiceBlocksSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = ServiceBlock

        fields = '__all__'

class ExtraServiceBlocksSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = ExtraServiceBlock

        fields = '__all__'

class CustomersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = Customer

        fields = '__all__'