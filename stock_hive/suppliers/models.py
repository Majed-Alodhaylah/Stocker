from django.db import models
from django.utils import timezone

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='suppliers/logos/', blank=True, null=True)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
