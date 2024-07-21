import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.nepsesimple import csv_json, plot_index_value_over_time,get_ipo_message,get_stock_details


def main():
    st.title("Nepal Stock Market Data")

    # # Get today's date in YEAR-MONTH-DAY format
    # today = datetime.date.today().strftime("%Y-%m-%d")
    
    # # Download the CSV file
    # df_out = runcmd(f'cat {today} || wget --no-check-certificate https://www.nepalstock.com.np/api/nots/market/export/todays-price/{today}', verbose=False)
    # #print(df_out)
    
    # df_out = asyncio.run(download_data())
    
    df = csv_json()
    
    # write the summary of the data in container with markdown
    
    
    c = st.container()
    c.markdown(f'''
            :red[Total Stocks]: {len(df)} 
            
            
            :green[Total Market Capitalization]: {df['Turnover'].sum()} 
            
            :orange[Total Traded Value]: {df['Trans.'].sum()} 
            
            :green[Total Traded Quantity]: {df['Vol'].sum()}
            
            ''')

    # Display IPO message
    st.title("IPO Events")
    url = "https://www.sharesansar.com/?show=home"
    message = get_ipo_message(url)
    st.markdown(message)
    
    # Load data from the URL
    url = "https://merolagani.com/Indices.aspx"
    df_plot = pd.read_html(url)[0]
    df_plot = df_plot.iloc[::-1].reset_index(drop=True)
    
    # plot candlestick chart of Index Value Over Time
    df_plot['Date (AD)'] = pd.to_datetime(df_plot['Date (AD)'])

    # create the row of Open, High, Low, Close
    df_plot['Open'] = df_plot['Index Value'] - df_plot['Absolute Change']
    df_plot['High'] = df_plot['Index Value'] + df_plot['Absolute Change']

    st.title("Index Value Over Time")
    fig = go.Figure(data=[go.Candlestick(x=df_plot['Date (AD)'],
                open=df_plot['Open'],
                high=df_plot['High'],
                low=df_plot['Open'],
                close=df_plot['Index Value'])])
    # plot moving average
    fig.add_trace(go.Scatter(x=df_plot['Date (AD)'], y=df_plot['Index Value'].rolling(window=5).mean(), mode='lines', name='Moving Average 5 Days'))

    st.plotly_chart(fig)
    
    # Call the function to display the plot
    # plot_index_value_over_time(df_plot)  
    
    # st.dataframe(df)
    # st display dataframe with color according to percentage change column value
    st.title("Today's Stock Market Data")
    st.dataframe(df) #.style.applymap(lambda x: 'color: red' if x < 0 else 'color: green', subset=['PERCENTAGE_CHANGE'])
    
    st.title("Top Gainers")
    top_gainers = df.head(10)
    # top_gainers = top_gainers.drop(columns=['BUSINESS_DATE','S.N','SECURITY_ID'])
    st.dataframe(top_gainers)
    
    st.title("Top Losers")
    top_losers = df.tail(10)
    # top_losers = top_losers.drop(columns=['BUSINESS_DATE','S.N','SECURITY_ID'])
    st.dataframe(top_losers)
    
    # sort by TOTAL_TRADED_QUANTITY
    st.title("Top Traded Quantity")
    top_traded_quantity = df.sort_values(by='Vol', ascending=False).head(10)
    # top_traded_quantity = top_traded_quantity.drop(columns=['BUSINESS_DATE','S.N','SECURITY_ID'])
    st.dataframe(top_traded_quantity)
    
    # sort by MARKET_CAPITALIZATION
    st.title("Top Market Capitalization")
    top_market_capitalization = df.sort_values(by='Turnover', ascending=False).head(10)
    # top_market_capitalization = top_market_capitalization.drop(columns=['BUSINESS_DATE','S.N','SECURITY_ID'])
    st.dataframe(top_market_capitalization)
    
    with st.sidebar:
        # make a search bar to search stock by columns name with dropdown of df['Symbol']
        st.title("Search Stock")
        stock_name = st.selectbox('Select Stock Symbol', df['Symbol'])
        get_stock_details(stock_name)
    

if __name__ == "__main__":
    main()
