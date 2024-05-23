from django.shortcuts import render
from .utils.utils import csv_json, get_ipo_message, get_stock_details
from ninja import NinjaAPI
# import logging
from django.contrib.auth.decorators import login_required
from .models import StockData, IPOEvents
from datetime import datetime
import numpy as np
import pandas as pd

# logger = logging.getLogger(__name__)

# Create your views here.
api = NinjaAPI()

@api.get("/stock_market")
def stock_market_view(request):
    
    # Get's Today date
    today = datetime.today().date()
    
    # Retrieve all objects for today's date
    stock_data_objects = StockData.objects.filter(date=today)
    
    if stock_data_objects.exists():
        # If data already exists for today, use the first object
        stock_data = stock_data_objects.first()
        total_stocks = stock_data.total_stocks
        total_market_cap = stock_data.total_market_cap
        total_traded_value = stock_data.total_traded_value
        total_traded_quantity = stock_data.total_traded_quantity
    else:
        # Calculate new data if no data exists for today
        df = csv_json()
        total_stocks = int(len(df))
        total_market_cap = float(df['Turnover'].sum())
        total_traded_value = float(df['Trans.'].sum())  # Corrected to float
        total_traded_quantity = float(df['Vol'].sum())  # Corrected to float
        data = np.array(df)
        columns = df.columns.tolist()
        
        # Create a new instance of StockMarket model
        stock_data = StockData(
            date=today,
            total_stocks=total_stocks,
            total_market_cap=total_market_cap,
            total_traded_value=total_traded_value,
            total_traded_quantity=total_traded_quantity,
            data = data,
            columns = columns
        )
        
        # Save the instance to the database
        stock_data.save()
    
    context = {
        'total_stocks': total_stocks,
        'total_market_cap': total_market_cap,
        'total_traded_value': total_traded_value,
        'total_traded_quantity': total_traded_quantity
    }
    
    return context

@api.get("/ipo_events")
def ipo_events_view(request):
    
    # Get's Today date
    today = datetime.today().date()
    
    # Check if the data is already saved in the database
    if not IPOEvents.objects.filter(date=today).exists():
        url = "https://www.sharesansar.com/?show=home"
        message = get_ipo_message(url)
    
        # create a new instance of IPOEvents model
        ipo_event = IPOEvents(
            date=today,
            message=message
        )
        
        # save the instance to the database
        ipo_event.save()
    else:
        # If data already exists for today, retrieve it from the database
        ipo_event = IPOEvents.objects.get(date=today)
        message = ipo_event.message
    
    return message


@api.get("/stock_market/{symbol}/today")
def stock_market_symbol_view(request, symbol: str):
    # Get's Today date
    today = datetime.today().date()
    
    # Retrieve all objects for today's date
    stock_data_objects = StockData.objects.filter(date=today)
    stock_data = stock_data_objects.first()
    data = stock_data.data
    columns = stock_data.columns
    df = pd.DataFrame(data, columns=columns)
    
    stock = df[df['Symbol'] == symbol]
    stock = stock.to_dict(orient='records')
    return stock[0]

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