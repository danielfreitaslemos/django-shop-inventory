from django.db import models

# Create your models here.

class Product(models.Model):
    # unique=True prevents two products from having the same barcode/code
    objects = models.Manager()

    product_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_count = models.IntegerField()

    def __str__(self):
        return f"{self.product_code} - {self.name}"
