from django.apps import AppConfig
from django.db.models.signals import post_save


class StrategyConfig(AppConfig):
    name = 'strategy'

    def ready(self):
        from strategy.models import Strategy
        from strategy.signals import create_orders
        # 注册信号
        post_save.connect(create_orders, sender=Strategy)
