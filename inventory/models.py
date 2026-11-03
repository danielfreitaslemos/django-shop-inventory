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

class SaleLog(models.Model):
    objects = models.Manager()

    # ForeignKey links each log to a specific product row.
        # SET_NULL ensures that if a product is deleted, the sales history is kept!

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)

    product_code = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale: {self.product_name} x{self.quantity} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
