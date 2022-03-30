from django import forms

class CategoryCreateForm(forms.Form):
    product_name = forms.CharField(label='Product name', max_length=100)
    product_code = forms.CharField(label='Product code', max_length=50, required=False)
    stock_quantity = forms.IntegerField(label='Stock quantity', )



