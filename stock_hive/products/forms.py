from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product
from inventory.models import StockMovement

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'reorder_level', 'quantity', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = (f.widget.attrs.get('class', '') + ' form-control').strip()

class MovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['quantity', 'unit_price', 'note']  
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'quantity': _('Quantity'),
            'unit_price': _('Unit Price'),
            'note': _('Notes'),
        }

    def clean_quantity(self):
        q = self.cleaned_data['quantity']
        if q is None or q <= 0:
            raise forms.ValidationError(_("Quantity must be positive"))
        return q
