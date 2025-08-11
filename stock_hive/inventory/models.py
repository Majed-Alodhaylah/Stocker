from django.db import models
from django.conf import settings

MOVEMENT_CHOICES = (
    ('IN', 'IN'),
    ('OUT', 'OUT'),
    ('ADJ', 'ADJ'),
)

class StockMovement(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='movements')
    kind = models.CharField(max_length=3, choices=MOVEMENT_CHOICES)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.kind} {self.quantity} of {self.product}'
