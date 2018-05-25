from django.db import models

# Create your models here.
from crypto_auto_trading import constants


class Symbol(models.Model):
    name = models.CharField(max_length=30)
    base_asset = models.CharField(max_length=15)
    quote_asset = models.CharField(max_length=15)
    min_qty = models.DecimalField(max_digits=14, decimal_places=8)
    min_price = models.DecimalField(max_digits=14, decimal_places=8)
    min_notional = models.DecimalField(max_digits=14, decimal_places=8)
    step_size = models.DecimalField(max_digits=14, decimal_places=8)

    def __str__(self):
        return self.name


class Strategy(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    side = models.CharField(max_length=10, choices=constants.SIDE_CHOICES)
    quantity = models.DecimalField(max_digits=14, decimal_places=8)
    base_price = models.DecimalField(max_digits=14, decimal_places=8, help_text='买入时的最高价或卖出时的最低价')
    start_dt = models.DateTimeField()
    end_dt = models.DateTimeField()

    def __str__(self):
        return '{}-{}'.format(self.side, self.symbol.name)


class Order(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    time = models.DateTimeField()
    quantity = models.DecimalField(max_digits=14, decimal_places=8)
    price = models.DecimalField(max_digits=14, decimal_places=8, null=True)
    is_valid = models.BooleanField()
    status = models.CharField(max_length=15, help_text="交易平台返回的状态", null=True)
    message = models.CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.strategy)
