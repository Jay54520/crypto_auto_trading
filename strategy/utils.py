# -*- coding: utf-8 -*-
from binance.client import Client
from django.conf import settings

client = Client(settings.API_KEY, settings.API_SECRET)
