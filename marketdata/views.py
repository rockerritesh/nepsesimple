from django.shortcuts import render
from .utils.utils import csv_json, get_ipo_message, get_stock_details
from ninja import NinjaAPI
import logging
from django.contrib.auth.decorators import login_required

# logger = logging.getLogger(__name__)

# Create your views here.
api = NinjaAPI()

@api.get("/stock_market")
def stock_market_view(request):
    df = csv_json()
    total_stocks = int(len(df))
    total_market_cap = float(df['Turnover'].sum())
    total_traded_value = int(df['Trans.'].sum())
    total_traded_quantity = int(df['Vol'].sum())
    context = {
        'total_stocks': total_stocks,
        'total_market_cap': total_market_cap,
        'total_traded_value': total_traded_value,
        'total_traded_quantity': total_traded_quantity
    }
    # logger.info(f"Total Stocks: {total_stocks}")
    # logger.info(f"Total Market Capitalization: {total_market_cap}")
    # logger.info(f"Total Traded Value: {total_traded_value}")
    # logger.info(f"Total Traded Quantity: {total_traded_quantity}")
    
    return context

@api.get("/ipo_events")
def ipo_events_view(request):
    url = "https://www.sharesansar.com/?show=home"
    message = get_ipo_message(url)
    return message

@api.get("/stock_market/{symbol}/today")
def stock_market_symbol_view(request, symbol: str):
    df = csv_json()
    stock = df[df['Symbol'] == symbol]
    stock = stock.to_dict(orient='records')
    return stock

@api.get("/stock_market/{symbol}/history")
def stock_market_symbol_history_view(request, symbol: str):
    df, _, _ = get_stock_details(symbol)
    stock = df.to_dict(orient='records')
    return stock

@login_required
@api.get("/stock_market/{symbol}/prediction")
def stock_market_symbol_prediction_view(request, symbol: str):
    _, predict, _ = get_stock_details(symbol)
    context = {
        'symbol': symbol,
        'prediction': predict
    }
    return context

@login_required
@api.get("/stock_market/{symbol}/plot")
def stock_market_symbol_plot_view(request, symbol: str):
    _, _, plot = get_stock_details(symbol)
    return plot