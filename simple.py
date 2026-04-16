#!/usr/bin/env python
# coding: utf-8
# Open the file in read mode
with open("docs/html.txt", "r") as f:
    # Read the contents of the file
    asadas = f.read()

# print(asadas)

import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import date

# import openpyxl
import matplotlib.pyplot as plt
import bs4
import html5lib

# import telegram
# from telegram import InputFile


# Load data from the URL
url = "https://merolagani.com/Indices.aspx"
df = pd.read_html(url)[0]
df = df.iloc[::-1].reset_index(drop=True)

# Create X and Y arrays for regression analysis
y = np.array(df["Index Value"])
x = np.linspace(1, len(y), len(y)).reshape(-1, 1)

# Perform linear regression on the data
reg = LinearRegression()
reg.fit(x, y)

# Predict the next data point using the linear regression model
next_index = reg.predict(np.array(len(y) + 1).reshape(1, -1))[0]

# Get today's date
today = date.today()
date_str = date.isoformat(today)

# Plot the data and regression line
plt.figure(figsize=(16, 8))
plt.plot(df["Date (AD)"], df["Index Value"], "bo-", label="Index Value")
plt.plot(date_str, next_index, "ro", label="Predicted Next Index Value")

# Add annotations
plt.annotate(
    f"Predicted: {next_index:.2f}",
    xy=(date_str, next_index),
    xytext=(-50, 30),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->", color="red"),
)
plt.annotate(
    f"Regression Line: {reg.coef_[0]:.2f}x + {reg.intercept_:.2f}",
    xy=(0.05, 0.95),
    xycoords="axes fraction",
    fontsize=12,
    ha="left",
    va="top",
)

# Add regression line
plt.plot(df["Date (AD)"], reg.predict(x), "g--", label="Regression Line")

# Format x-axis
plt.xticks(rotation=45, ha="right")
plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))

plt.xlabel("Date")
plt.ylabel("Index Value")
plt.title("Nepal Stock Exchange NEPSE Index Value")
plt.legend()
plt.grid()
plt.savefig("docs/graph.png")
plt.show()


# FOR STOCK

urlstock = "https://www.sharesansar.com/market"
htmlstock = requests.get(urlstock).content
df_list_stock = pd.read_html(htmlstock)

df_stock = df_list_stock[3]
df_stock.to_csv("docs/stock.csv")
stok_html = df_stock.to_html()
# df_stock.to_html("stock.html")
# df_stock

# make stock.html by appending asadas and stok_html
stok_html = asadas + stok_html + "</body> </html>"

# save stock.html
with open("docs/stock.html", "w") as output:
    output.write(stok_html)


top_trans = df_list_stock[-2].to_html()
# append asadas with top_trans and save as toptransactions.html
html = asadas + str(top_trans) + "</body> </html>"
with open("docs/toptransactions.html", "w") as output:
    output.write(html)


top_volum = df_list_stock[-3].to_html()
# append asadas with top_volum and save as topvolume.html
html = asadas + str(top_volum) + "</body> </html>"
with open("docs/topvolume.html", "w") as output:
    output.write(html)


gold = df_list_stock[-7].to_html()
# append asadas with gold and save as gold.html
html = asadas + str(gold) + "</body> </html>"
with open("docs/gold.html", "w") as output:
    output.write(html)


compare = df_list_stock[-8].to_html("compare.html")
# append asadas with compare and save as compare.html
html = asadas + str(compare) + "</body> </html>"
with open("docs/compare.html", "w") as output:
    output.write(html)


index = df_list_stock[-12].to_html()

# === JSON EXPORTS ===
import json
from datetime import date as _date

_today = _date.today().isoformat()

# Export index data as JSON
# df_list_stock[-12] has columns: Index, Open, High, Low, Close, Point Change, % Change, Turnover
_index_df = df_list_stock[-12]
_index_records = []
for _, row in _index_df.iterrows():
    _index_records.append({
        "name": str(row.get("Index", "")),
        "open": float(row.get("Open", 0)),
        "high": float(row.get("High", 0)),
        "low": float(row.get("Low", 0)),
        "current": float(row.get("Close", 0)),
        "points_change": float(row.get("Point Change", 0)),
        "pct_change": float(row.get("% Change", 0)),
        "turnover": float(row.get("Turnover", 0)),
    })

# Sub-indices from table 3
_sub_index_df = df_list_stock[3]
_sub_records = []
for _, row in _sub_index_df.iterrows():
    _sub_records.append({
        "name": str(row.iloc[0]) if len(row) > 0 else "",
        "current": float(row.iloc[1]) if len(row) > 1 else 0,
        "points_change": float(row.iloc[2]) if len(row) > 2 else 0,
        "pct_change": float(row.iloc[3]) if len(row) > 3 else 0,
    })

_index_data = {
    "date": _today,
    "primary": _index_records,
    "sub_indices": _sub_records,
}
with open("docs/index_data.json", "w") as f:
    json.dump(_index_data, f, indent=2)

# Export market summary (gainers, losers, turnover, volume) as JSON
def _parse_gainer_loser(df):
    records = []
    for _, row in df.iterrows():
        records.append({
            "symbol": str(row.iloc[0]) if len(row) > 0 else "",
            "ltp": float(row.iloc[1]) if len(row) > 1 else 0,
            "point_change": float(row.iloc[2]) if len(row) > 2 else 0,
            "pct_change": float(row.iloc[3]) if len(row) > 3 else 0,
        })
    return records

def _parse_turnover(df):
    records = []
    for _, row in df.iterrows():
        records.append({
            "symbol": str(row.iloc[0]) if len(row) > 0 else "",
            "turnover": float(row.iloc[1]) if len(row) > 1 else 0,
            "ltp": float(row.iloc[2]) if len(row) > 2 else 0,
        })
    return records

def _parse_volume(df):
    records = []
    for _, row in df.iterrows():
        records.append({
            "symbol": str(row.iloc[0]) if len(row) > 0 else "",
            "volume": float(row.iloc[1]) if len(row) > 1 else 0,
            "ltp": float(row.iloc[2]) if len(row) > 2 else 0,
        })
    return records

_market_summary = {
    "date": _today,
    "top_gainers": _parse_gainer_loser(df_list_stock[-6]),
    "top_losers": _parse_gainer_loser(df_list_stock[-5]),
    "top_turnover": _parse_turnover(df_list_stock[-4]),
    "top_volume": _parse_volume(df_list_stock[-3]),
}
with open("docs/market_summary.json", "w") as f:
    json.dump(_market_summary, f, indent=2)

print(f"[JSON] Exported index_data.json ({len(_index_records)} primary, {len(_sub_records)} sub-indices)")
print(f"[JSON] Exported market_summary.json ({len(_market_summary['top_gainers'])} gainers, {len(_market_summary['top_losers'])} losers)")
# === END JSON EXPORTS ===

urlshare = "https://www.sharesansar.com/?show=home"
htmlshare = requests.get(urlshare).content
df_list_share = pd.read_html(htmlshare)
df_share = df_list_share[2]

# df_share.to_html("ipo.html")
# df_list_share[1].to_html("bonous.html")
# df_list_share[4].to_html("newsofbank.html")
# df_list_share[5].to_html("stock.html")
# df_list_share[6].to_html("gradeofcompany.html")
# df_list_share[7].to_html("companymerged.html")
# df_list_share[0].to_html("bookclosure.html")

# merge df_list_share[7] to df_list_share[0] and save as details.html with appropriate html tags
html = (
    asadas
    + str("<h2> Share </h2>")
    + str(df_share.to_html())
    + str("<h2> Bonous </h2>")
    + str(df_list_share[1].to_html())
    + str("<h2> News of Bank </h2>")
    + str(df_list_share[4].to_html())
    + str("<h2> Stock </h2>")
    + str(df_list_share[5].to_html())
    + str("<h2> Grade of Company </h2>")
    + str(df_list_share[6].to_html())
    + str("<h2> Company Merged </h2>")
    + str(df_list_share[7].to_html())
    + str("<h2> Book Closure </h2>")
    + str(df_list_share[0].to_html())
    + "</body> </html>"
)
with open("docs/details.html", "w") as output:
    output.write(html)


# json file nepssimpleeapi
df = pd.read_html("https://www.sharesansar.com/today-share-price")
df = df[-1].T
# Send a message to the chat using the chat ID
# bot.send_message(chat_id=CHAT_ID, text=df.to_csv())

df.to_json("docs/nepsesimple.json")
html = df.T.to_html()
html = asadas + index + html + "</body> </html>"
with open("docs/index.html", "w") as output:
    output.write(html)
