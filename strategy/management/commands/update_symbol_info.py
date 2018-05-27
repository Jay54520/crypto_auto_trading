# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from strategy.utils import update_symbol_info


class Command(BaseCommand):
    help = '更新火币 symbol 信息到 Symbol model'

    def handle(self, *args, **options):
        update_symbol_info()
        self.stdout.write('完成更新 symbol 信息')
