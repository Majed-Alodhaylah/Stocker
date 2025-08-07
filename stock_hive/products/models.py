from django.db import models
from categories.models import Category
from suppliers.models import Supplier
from datetime import date

class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    suppliers = models.ManyToManyField(Supplier, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='products/images/', blank=True, null=True)

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.quantity < 5

    def is_expired(self):
        return self.expiry_date and self.expiry_date < date.today()
