from django.shortcuts import render
from .models import Product, StoreLocation, Supplier, ProductCategory
from django.contrib import messages
from customers.models import SalonAccount
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound

# Create your views here.


def create_store_location(request):
    salon = request.user.salonAcc
    storeLocations = StoreLocation.objects.filter(salon=salon)
    _popup = request.GET.get('_popup')
    print(_popup)
    context = {
        'storeLocations':storeLocations,
        'popup':_popup
    }
    if request.method == 'POST':
        reqst = request.POST
        try:
            StoreLocation(salon=salon, location=reqst['location'], shelf=reqst['shelf'], box=reqst['box']).save()
            messages.info(request, 'Store Location {} {} {} created'.format(reqst['location'], reqst['shelf'], reqst['box']))
            return render(request, 'inventory/create_store_location.html', context)
        except:
            messages.error(request, 'Store Location {} {} {} already exit'.format(reqst['location'], reqst['shelf'], reqst['box']))
            return render(request, 'inventory/create_store_location.html', context)
    else:

        return render(request, 'inventory/create_store_location.html', context)
from .forms import CategoryCreateForm
def create_category(request):
    form = CategoryCreateForm()
    return render (request, 'inventory/create_category.html', {'form':form} )
def create_product(request):
    salon = request.user.salonAcc
    storeLocations = StoreLocation.objects.filter(salon=salon)
    products = Product.objects.filter(salon=salon).order_by('-stockInTime')[:20]
    context = {
        'products':products,
        'storeLocations':storeLocations
    }
    if request.method == 'POST':
        reqst = request.POST
        try:
            product = Product(salon=salon,
                    productName=reqst['productName'],
                    productCode=reqst['productCode'],
                    unit=reqst['unit'],
                    stockQuantity=reqst['stockQuantity'],
                    lowStock=reqst['lowStock'],
                
                    decription=reqst['decription'],
                    
                    storeLocation=StoreLocation.objects.filter(pk=reqst['storeLocation']).first(),
                    
                    )
            if reqst['supplier']:
                product.supplier=Supplier.objects.filter(pk=reqst['supplier']).first(),
            if reqst['category']:
                product.category=ProductCategory.objects.filter(pk=reqst['category']).first(),
            if reqst['orderTime']:
                product.orderTime=datetime.strptime(reqst['orderTime'], '%Y-%m-%d')
            if reqst['stockInTime']:
                product.stockInTime=datetime.strptime(reqst['stockInTime'], '%Y-%m-%d')
            if reqst['sellPrice']:
                product.sellPrice=float(reqst['sellPrice'])
            if reqst['buyPrice']:
                product.buyPrice=float(reqst['buyPrice'])
            if reqst['quanlity']:
                product.quanlity=reqst['quanlity']

            product.save()
            messages.info(request, 'Product {} {} created'.format(reqst['productName'], reqst['productCode']))
            return render(request, 'inventory/create_product.html', context)
        except:
            # messages.error(request, 'Product {} {} already exit'.format(reqst['productName'], reqst['productCode']))
            return render(request, 'inventory/create_product.html', context)
    else:

        return render(request, 'inventory/create_product.html', context)

def list_products(request):
    salon = request.user.salonAcc
    products = Product.objects.filter(salon=salon)
    context = {
        "products":products
    }
    return JsonResponse(context)