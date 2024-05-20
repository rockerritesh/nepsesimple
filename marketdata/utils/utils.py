import pandas as pd
import requests
import plotly.graph_objects as go

def csv_json():

    # json file nepssimpleeapi
    df = pd.read_html("https://www.sharesansar.com/today-share-price")
    df = df[-1]

    # add a cloumn percentage change which does calculation like (close-open)/open*100
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df["Prev. Close"] = pd.to_numeric(df["Prev. Close"], errors="coerce")
    df["Turnover"] = pd.to_numeric(df["Turnover"], errors="coerce")
    df["Vol"] = pd.to_numeric(df["Vol"], errors="coerce")
    df["Trans."] = pd.to_numeric(df["Trans."], errors="coerce")

    df["PERCENTAGE_CHANGE"] = (df["Close"] - df["Open"]) / df["Close"] * 100

    df = df.sort_values(by="PERCENTAGE_CHANGE", ascending=False)

    # df.to_json(json_file, orient='records')
    # json_respons  = df.to_json(orient='records')

    return df


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
        message = "No IPO event\n" + "_" * len("No IPO event\n")
    else:
        # Filter IPOs that are currently open
        filtered_df_open = df_ipo[df_ipo["Status"].isin(["Open"])][
            ["Company", "Units", "Price", "Opening Date", "Closing Date", "Status"]
        ]

        # Filter IPOs that are coming soon
        filtered_df_coming_soon = df_ipo[df_ipo["Status"].isin(["Coming Soon"])][
            ["Company", "Units", "Price", "Opening Date", "Closing Date", "Status"]
        ]

        # Construct message for open IPOs
        if len(filtered_df_open) > 0:
            message += f"IPOs Opens:\n" + "_" * len("IPOs Opens:\n")
            for _, row in filtered_df_open.iterrows():
                message += f"\n\n{row['Company']}\nUnits: {row['Units']}\nPrice: {row['Price']}\nOpening Date: {row['Opening Date']}\nClosing Date: {row['Closing Date']}\n\n"

        # Construct message for IPOs coming soon
        if len(filtered_df_coming_soon) > 0:
            message += f"IPOs Coming Soon:\n" + "_" * len("IPOs Coming Soon:\n")
            for _, row in filtered_df_coming_soon.iterrows():
                message += f"\n\n{row['Company']}\nUnits: {row['Units']}\nPrice: {row['Price']}\nOpening Date: {row['Opening Date']}\nClosing Date: {row['Closing Date']}"

    return message if len(message) > 0 else "No IPO event"


# prediction function
def predict_price(df):
    # convert to float
    # make numTrans and tradedShares as float
    df["numTrans"] = df["numTrans"].astype(float)
    df["tradedShares"] = df["tradedShares"].astype(float)
    df["amount"] = df["amount"].astype(float)
    # Calculate statistical measures
    stats = df.describe()

    # Predict the next index based on the trend observed in the provided data
    last_close = df["close"].iloc[-1]
    mean_close = stats.loc["mean", "close"]
    mean_prev_close = stats.loc["mean", "prevClose"]
    next_index = last_close + (mean_close - mean_prev_close)
    
    return next_index


def get_stock_details(stock_name):
    # Fetch the JSON data
    json_out = requests.get(
        f"https://the-value-crew.github.io/nepse-api/data/company/{stock_name}.json"
    )

    json_out = json_out.json()

    # Convert JSON data into a DataFrame
    df = pd.DataFrame(json_out).T

    # Convert the nested 'price' dictionaries into separate columns
    price_df = df["price"].apply(pd.Series)

    # Concatenate the original DataFrame with the new 'price' DataFrame
    df = pd.concat([df.drop("price", axis=1), price_df], axis=1)

    # first column name is the date
    df.index.name = "Date"

    # Predictions
    predict = predict_price(df)
    
    # Drop nan values according to the 'open' column
    df_nan = df.dropna(subset=["open"])

    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df_nan.index,
            open=df_nan["open"],
            high=df_nan["max"],
            low=df_nan["min"],
            close=df_nan["close"],
        )
    )

    return df, predict, fig.to_json()

