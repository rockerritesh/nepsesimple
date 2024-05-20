from django.urls import path
from .views import stock_market_view

urlpatterns = [
    path('', stock_market_view, name='stock_market'),
]