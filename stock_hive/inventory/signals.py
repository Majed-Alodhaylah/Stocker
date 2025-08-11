from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StockMovement
from products.models import Product

@receiver(post_save, sender=StockMovement)
def update_product_quantity(sender, instance, created, **kwargs):
    if not created:
        return
    p: Product = instance.product
    if instance.kind == 'IN':
        p.quantity += instance.quantity
    elif instance.kind == 'OUT':
        p.quantity = max(0, p.quantity - instance.quantity)
    else:  # ADJ
        p.quantity += instance.quantity
    p.save(update_fields=['quantity'])
