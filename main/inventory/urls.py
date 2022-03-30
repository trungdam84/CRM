from django.urls import path, include
from django.conf.urls import url
from .views import  create_category, create_store_location, create_product, list_products



urlpatterns = [
    path('create-store-location/', create_store_location, name='create_store_location'),
    path('create-product/', create_product, name='create_product'),
    path('get-products/', list_products, name='get_products'),
    path('create-category/', create_category, name='create-category'),
]