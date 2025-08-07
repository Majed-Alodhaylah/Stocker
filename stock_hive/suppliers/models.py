from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='suppliers/logos/', blank=True, null=True)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name
