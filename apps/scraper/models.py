from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    review_count = models.PositiveIntegerField(default=0)
    images = models.TextField()

    def __init__(self, *args, **kwargs):
        return self.title
