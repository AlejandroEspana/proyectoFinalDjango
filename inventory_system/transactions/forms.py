from django import forms
from .models import Transaction
from inventory.models import Product

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['product', 'transaction_type', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'id': 'id_product'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_transaction_type'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'id_quantity'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'id': 'id_unit_price'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aseguramos ordenar los productos por nombre
        self.fields['product'].queryset = Product.objects.all().order_by('name')
