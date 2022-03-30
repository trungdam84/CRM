from django.db import models
from customers.models import SalonAccount

# Create your models here.
class StoreLocation(models.Model):
    salon = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    location = models.CharField(max_length=25)
    shelf = models.CharField(max_length=4)
    box = models.CharField(max_length=4)
    class Meta:
        unique_together = ('salon', 'location', 'shelf', 'box')
    
    def __str__(self):
        return f'{self.location} {self.shelf} {self.box}'

class ProductCategory(models.Model):
    salon = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    categoryName = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name_plural = "Product categories"
    def __str__(self):
        return f'{self.categoryName}'
class Supplier(models.Model):
    salon = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    supplierName = models.CharField(max_length=50)
    supplierTel = models.CharField(max_length=15)
    supplierEmail = models.CharField(max_length=100, null=True, blank=True)
    supplierAddress1 = models.CharField(max_length=100, null=True, blank=True)
    supplierTown = models.CharField(max_length=100, null=True, blank=True)
    supplierCounty = models.CharField(max_length=100, null=True, blank=True)
    supplierPostCode = models.CharField(max_length=10, null=True, blank=True)
    supplierCountry = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f'{self.supplierName}'
    class Meta:
        unique_together = ('salon', 'supplierName')
        unique_together = ('salon', 'supplierTel')
class Product(models.Model):
    QUALITY_CHOICES = (

        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
        )
    salon = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
    productName = models.CharField(max_length=250)
    productCode = models.CharField(max_length=50)
    unit = models.CharField(max_length=50,)
    stockQuantity = models.PositiveSmallIntegerField()
    orderTime = models.DateField(null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    sellPrice = models.FloatField(null=True, blank=True)
    buyPrice = models.FloatField(null=True, blank=True)
    stockInTime = models.DateField(null=True, blank=True)
    decription = models.TextField(null=True, blank=True)
    quanlity = models.PositiveSmallIntegerField(choices=QUALITY_CHOICES, blank=True, null=True)
    storeLocation = models.ForeignKey(StoreLocation, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True)
    lowStock = models.PositiveSmallIntegerField()
    
    class Meta:

        unique_together = ('salon', 'productName', 'productCode', 'supplier')
    def __str__(self):
        return f'{self.productName}'
    

    def save(self, *args, **kwargs):
        if self.sellPrice:
            self.sellPrice = round(self.sellPrice, 2)
        if self.buyPrice:
            self.buyPrice = round(self.buyPrice, 2)
        super(Product, self).save(*args, **kwargs)