import streamlit as st
# import wget
import requests
import subprocess
import pandas as pd
import csv
import asyncio
import datetime
import matplotlib.pyplot as plt

# async def runcmd(cmd, verbose=True):
#     process = subprocess.Popen(
#         cmd,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#         shell=True
#     )
#     std_out, std_err = process.communicate()
#     if verbose:
#         st.write(std_out.strip(), std_err)
#     return std_out.strip()



# async def download_data():
#     today = datetime.date.today().strftime("%Y-%m-%d")
#     yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
#     past_date = datetime.date.today() - datetime.timedelta(days=2)
    
#     while True:
#         # Check if today's file is empty
#         df_data = await runcmd(f'cat {today} || wget --no-check-certificate https://www.nepalstock.com.np/api/nots/market/export/todays-price/{today}', verbose=False)
#         await asyncio.sleep(5)  # Adjust sleep time as needed
#         # print(today)
#         if df_data.strip() == '':
#             # Today's file is empty, let's try yesterday
#             df_data = await runcmd(f'cat {yesterday} || wget --no-check-certificate https://www.nepalstock.com.np/api/nots/market/export/todays-price/{yesterday}', verbose=False)
#             await asyncio.sleep(5)  # Adjust sleep time as needed
#             # print(yesterday)
#             if df_data.strip() == '':
#                 # Yesterday's file is also empty, fetch past day's data
#                 past_date_str = past_date.strftime("%Y-%m-%d")
#                 df_data = await runcmd(f'cat {past_date_str} || wget --no-check-certificate https://www.nepalstock.com.np/api/nots/market/export/todays-price/{past_date_str}', verbose=False)
#                 # Update past_date for next iteration
#                 past_date -= datetime.timedelta(days=1)
#                 # print(past_date)
#                 # Sleep for some time to avoid flooding requests
#                 await asyncio.sleep(5)  # Adjust sleep time as needed
#             else:
#                 break  # Exit loop if yesterday's data is found
#         else:
#             break  # Exit loop if today's data is found
#     # print(df_data)
#     return df_data

def csv_json():
    # with open(csv_file, 'r') as file:
    # reader = csv.reader(csv_file)
    # reader = csv.reader(csv_file.splitlines())
    # data = list(reader)
    
    # # check the length of each row
    # length = []
    # for row in data:
    #     length.append(len(row))
    # #print(length)
    
    # # append to make pandas dataframe
    # df = pd.DataFrame(data)
    # df.columns = df.iloc[0]
    # df = df[1:]
    # # drop None columns
    # df = df.drop(columns=[None])
    
    # json file nepssimpleeapi
    df = pd.read_html("https://www.sharesansar.com/today-share-price")
    df = df[-1]

    # add a cloumn percentage change which does calculation like (close-open)/open*100
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Prev. Close'] = pd.to_numeric(df['Prev. Close'], errors='coerce')
    df['Turnover'] = pd.to_numeric(df['Turnover'], errors='coerce')
    df['Vol'] = pd.to_numeric(df['Vol'], errors='coerce')
    df['Trans.'] = pd.to_numeric(df['Trans.'], errors='coerce')

    df['PERCENTAGE_CHANGE'] = (df['Close'] - df['Open']) / df['Close'] * 100

    df = df.sort_values(by='PERCENTAGE_CHANGE', ascending=False)
    
    # df.to_json(json_file, orient='records')
    # json_respons  = df.to_json(orient='records')
    
    return df


def display_details(stock):
    st.write(f"**Name:** {stock['Symbol']}")
    # st.write(f"**Security Name:** {stock['SECURITY_NAME']}")
    st.write(f"**Open Price:** {stock['Open']}")
    st.write(f"**Close Price:** {stock['Close']}")
    st.write(f"**High Price:** {stock['High']}")
    st.write(f"**Low Price:** {stock['Low']}")
    st.write(f"**Total Traded Quantity:** {stock['Vol']}")
    st.write(f"**Total Traded Value:** {stock['Turnover']}")
    st.write(f"**Previous Day Close Price:** {stock['Prev. Close']}")
    st.write(f"**Fifty Two Weeks High:** {stock['52 Weeks High']}")
    st.write(f"**Fifty Two Weeks Low:** {stock['52 Weeks Low']}")
    # st.write(f"**Last Updated Time:** {stock['LAST_UPDATED_TIME']}")
    # st.write(f"**Last Updated Price:** {stock['LAST_UPDATED_PRICE']}")
    st.write(f"**Total Trades:** {stock['Trans.']}")
    # st.write(f"**Average Traded Price:** {stock['AVERAGE_TRADED_PRICE']}")
    # st.write(f"**Market Capitalization:** {stock['MARKET_CAPITALIZATION']}")
    # Add percentage change with color if it is positive or negative
    if stock['PERCENTAGE_CHANGE'] > 0:
        st.write(f"**Percentage Change:** <span style='color:green'>{stock['PERCENTAGE_CHANGE']}</span>", unsafe_allow_html=True)
    else:
        st.write(f"**Percentage Change:** <span style='color:red'>{stock['PERCENTAGE_CHANGE']}</span>", unsafe_allow_html=True)
        
def plot_index_value_over_time(df):
    # Convert 'Date (AD)' column to datetime format
    df['Date (AD)'] = pd.to_datetime(df['Date (AD)'])

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date (AD)'], df['Index Value'], marker='o', linestyle='-', color='b', label='Index Value')
    plt.xlabel('Date')
    plt.ylabel('Index Value')
    plt.title('Index Value Over Time')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Adding secondary y-axis for absolute change
    plt.twinx()
    plt.plot(df['Date (AD)'], df['Absolute Change'], marker='s', linestyle='-', color='r', label='Absolute Change')
    plt.ylabel('Absolute Change')
    plt.legend(loc='upper left')

    plt.tight_layout()
    
    # Display plot in Streamlit
    st.pyplot(plt)
    
# @st.cache_data
def get_ipo_message(url):
    # Fetch HTML content from the URL
    html = requests.get(url).content
    
    # Read HTML tables into a list of DataFrame objects
    df_list = pd.read_html(html)
    
    # Select the DataFrame containing IPO events
    df_ipo = df_list[2]
    
    # Initialize the message
    message = ""
    
    # Check if there are any IPO events
    if len(df_ipo) == 0:
        message = "No IPO event\n" + "_"*len("No IPO event\n")
    else:
        # Filter IPOs that are currently open
        filtered_df_open = df_ipo[df_ipo['Status'].isin(['Open'])][['Company', 'Units', 'Price', 'Opening Date', 'Closing Date', 'Status']]
        
        # Filter IPOs that are coming soon
        filtered_df_coming_soon = df_ipo[df_ipo['Status'].isin(['Coming Soon'])][['Company', 'Units', 'Price', 'Opening Date', 'Closing Date', 'Status']]
        
        # Construct message for open IPOs
        if len(filtered_df_open) > 0:
            message += f"IPOs Opens:\n" + "_"*len("IPOs Opens:\n")
            for _, row in filtered_df_open.iterrows():
                message += f"\n\n{row['Company']}\nUnits: {row['Units']}\nPrice: {row['Price']}\nOpening Date: {row['Opening Date']}\nClosing Date: {row['Closing Date']}\n\n"
        
        # Construct message for IPOs coming soon
        if len(filtered_df_coming_soon) > 0:
            message += f"IPOs Coming Soon:\n" + "_"*len("IPOs Coming Soon:\n")
            for _, row in filtered_df_coming_soon.iterrows():
                message += f"\n\n{row['Company']}\nUnits: {row['Units']}\nPrice: {row['Price']}\nOpening Date: {row['Opening Date']}\nClosing Date: {row['Closing Date']}"
    
    return message



def get_stock_details(stock_name):
    # Fetch the JSON data
    json_out = requests.get(f'https://the-value-crew.github.io/nepse-api/data/company/{stock_name}.json')
    
    json_out = json_out.json()
    
    # Convert JSON data into a DataFrame
    df = pd.DataFrame(json_out).T

    # Convert the nested 'price' dictionaries into separate columns
    price_df = df['price'].apply(pd.Series)

    # Concatenate the original DataFrame with the new 'price' DataFrame
    df = pd.concat([df.drop('price', axis=1), price_df], axis=1)
    
    # first column name is the date
    df.index.name = 'Date'
    
    # Display the DataFrame
    st.write(df)

    # Display box plots
    st.title('Trade Data Box Plots')
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    # Close Price Box Plot
    axs[0].boxplot(df['close'])
    axs[0].set_title('Close Price Box Plot')
    axs[0].set_xticklabels(['Close'])

    # Traded Shares Box Plot
    axs[1].boxplot(df['tradedShares'])
    axs[1].set_title('Traded Shares Box Plot')
    axs[1].set_xticklabels(['Traded Shares'])

    plt.tight_layout()
    st.pyplot(fig)
    
    # Display subplots
    st.title('Trade Data Subplots')
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    # Traded Shares vs Date
    axs[0].plot(df.index, df['tradedShares'], marker='o', linestyle='-')
    axs[0].set_title('Traded Shares vs Date')
    axs[0].set_xlabel('Date')
    axs[0].set_ylabel('Traded Shares')

    # Close vs Date
    axs[1].plot(df.index, df['close'], marker='o', linestyle='-')
    axs[1].set_title('Close vs Date')
    axs[1].set_xlabel('Date')
    axs[1].set_ylabel('Close Price')

    # Rotate x-axis ticks for better readability
    for ax in axs:
        ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    st.pyplot(fig)

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
    
    # Call the function to display the plot
    st.title("Index Value Over Time")
    plot_index_value_over_time(df_plot)  
    
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
    
    # make a search bar to search stock by columns name with dropdown of df['Symbol']
    st.title("Search Stock")
    stock_name = st.selectbox('Select Stock Symbol', df['Symbol'])
    get_stock_details(stock_name)
    

if __name__ == "__main__":
    main()
