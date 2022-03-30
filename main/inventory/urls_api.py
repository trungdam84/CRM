from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers
from .views_api import *


product_router = routers.DefaultRouter()
product_router.register(r'products', ProductViewSet)

product_category_router = routers.DefaultRouter()
product_category_router.register(r'product-categories', ProductCategoryViewSet)

store_location = routers.DefaultRouter()
store_location.register(r'store-locations', StoreLocationViewSet)

supplier = routers.DefaultRouter()
supplier.register(r'supplier', SupplierViewSet)
# stylists_router = routers.DefaultRouter()
# stylists_router.register(r'stylists', StylistsViewSet)
# service_blocks_router = routers.DefaultRouter()
# service_blocks_router.register(r'service-blocks', ServiceBlocksViewSet)
# extra_service_blocks_router = routers.DefaultRouter()
# extra_service_blocks_router.register(r'extra-service-blocks', ExtraServiceBlocksViewSet)
# salons_opening_times_router = routers.DefaultRouter()
# salons_opening_times_router.register(r'salons-opening-times', GenaralOpenTimesViewSet)
# weekly_close_day_router = routers.DefaultRouter()
# weekly_close_day_router.register(r'weekly-close-days', WeeklyCloseDaysViewSet)
# pedicure_chairs_router = routers.DefaultRouter()
# pedicure_chairs_router.register(r'pedicure-chairs', PedicureChairsViewSet)
# available_times_router = routers.DefaultRouter()
# available_times_router.register(r'available-times', AvailableTimesViewSet)
# opening_times_router = routers.DefaultRouter()
# opening_times_router.register(r'opening-times', OpenTimesViewSet)
# customers_router = routers.DefaultRouter()
# customers_router.register(r'customers', CustomersViewSet)
# queuesms_router = routers.DefaultRouter()
# queuesms_router.register(r'queuesms', QueueSMSViewSet)





urlpatterns = [

    path('', include(product_router.urls)),
    path('', include(product_category_router.urls)),
    path('', include(store_location.urls)),
    path('', include(supplier.urls)),
    # path('', include(stylists_router.urls)),
    # path('', include(service_blocks_router.urls)),
    # path('', include(extra_service_blocks_router.urls)),
    # path('', include(salons_opening_times_router.urls)),
    # path('', include(weekly_close_day_router.urls)),
    # path('', include(pedicure_chairs_router.urls)),
    # path('', include(available_times_router.urls)),
    # path('', include(opening_times_router.urls)),
    # path('', include(customers_router.urls)),
    # path('', include(queuesms_router.urls)),

    # path('salons/', SalonViewSet.as_view(),  name='salons'),
    # path('stylists/', StylistViewSet.as_view(), name='stylists'),
]