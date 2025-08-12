from django import forms
from .models import Product

MOVEMENT_CHOICES = (
    ("IN", "Stock In"),
    ("OUT", "Stock Out"),
    ("ADJ", "Adjust to Count"),
)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "description", "category", "suppliers",
            "price", "quantity", "reorder_level", "expiry_date", "image",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "suppliers": forms.SelectMultiple(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "reorder_level": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "expiry_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

class StockAdjustForm(forms.Form):
    kind = forms.ChoiceField(choices=MOVEMENT_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    quantity = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={"class": "form-control"}))
    unit_price = forms.DecimalField(required=False, min_value=0, decimal_places=2, max_digits=10,
                                    widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}))
    note = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
