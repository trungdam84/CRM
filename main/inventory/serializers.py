from .models import Product, StoreLocation, ProductCategory, Supplier
from rest_framework import serializers

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = Product

        fields = '__all__'


class StoreLocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = StoreLocation

        fields = '__all__'

class ProductCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = ProductCategory

        fields = '__all__'

class SupplierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:

        model = Supplier

        fields = '__all__'
