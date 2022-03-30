from django.contrib import admin
from .models import Product, StoreLocation, ProductCategory


class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields if field.name != "id"]

class StoreLocationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StoreLocation._meta.fields if field.name != "id"]

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductCategory._meta.fields if field.name != "id"]
# Register your models here.
# admin.site.register(StoreLocation, StoreLocationAdmin)
# admin.site.register(Product, ProductAdmin)
# admin.site.register(ProductCategory, ProductCategoryAdmin)
