from django.db import models


# Create your models here.

class Strategy(models.Model):
    symbol = models.CharField(max_length=30)
    quantity = models.DecimalField(max_digits=14, decimal_places=8)
    start_dt = models.DateTimeField()
    end_dt = models.DateTimeField()
