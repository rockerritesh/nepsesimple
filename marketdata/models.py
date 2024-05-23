from django.db import models
from picklefield.fields import PickledObjectField

class StockData(models.Model):
    date = models.DateField(auto_now_add=True)
    total_stocks = models.IntegerField()
    total_market_cap = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_traded_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_traded_quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    data = PickledObjectField()
    columns = PickledObjectField()

class IPOEvents(models.Model):
    date = models.DateField(auto_now_add=True)
    message = models.TextField()

class StockDetails(models.Model):
    date = models.DateField(auto_now_add=True)
    symbol = models.CharField(max_length=10)
    conf = models.FloatField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    vwap = models.FloatField()
    vol = models.IntegerField()
    prev_close = models.FloatField()
    turnover = models.FloatField()
    trans = models.IntegerField()
    diff = models.FloatField()
    range = models.FloatField()
    diff_percentage = models.FloatField()
    range_percentage = models.FloatField()
    vwap_percentage = models.FloatField()
    days_120 = models.FloatField()
    days_180 = models.FloatField()
    weeks_high = models.FloatField()
    weeks_low = models.FloatField()
    percentage_change = models.FloatField()