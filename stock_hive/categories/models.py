from django.db import models

class Category(models.Model):
    SEGMENT_CHOICES = [
        ("grocery", "Grocery / بقالة"),
        ("ecom", "E-commerce / متجر إلكتروني"),
    ]
    name = models.CharField(max_length=100, unique=True)
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, default="grocery")

    def __str__(self):
        return self.name
