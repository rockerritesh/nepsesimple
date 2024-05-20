from django.db import models

# Create your models here.
class StockData(models.Model):
    # date = models.DateField()
    volume = models.IntegerField()
    turnover = models.FloatField()
    transaction = models.IntegerField()
    symbol = models.CharField(max_length=10)
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    open = models.FloatField()
    