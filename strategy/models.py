from django.db import models


# Create your models here.

class Symbol(models.Model):
    name = models.CharField(max_length=30)
    base_asset = models.CharField(max_length=15)
    quote_asset = models.CharField(max_length=15)
    min_qty = models.DecimalField(max_digits=14, decimal_places=8)
    min_price = models.DecimalField(max_digits=14, decimal_places=8)
    min_notional = models.DecimalField(max_digits=14, decimal_places=8)
    step_size = models.DecimalField(max_digits=14, decimal_places=8)


class Strategy(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=14, decimal_places=8)
    start_dt = models.DateTimeField()
    end_dt = models.DateTimeField()


class Order(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    time = models.DateTimeField()
    quantity = models.DecimalField(max_digits=14, decimal_places=8)
    price = models.DecimalField(max_digits=14, decimal_places=8)
    is_valid = models.BooleanField()
    status = models.CharField(max_length=15, help_text="交易平台返回的状态")
    message = models.CharField(max_length=255)
