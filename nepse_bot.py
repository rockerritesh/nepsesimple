import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import bs4
import html5lib
import telegram
from telegram import InputFile

# ----MY----
BOT_TOKEN = '5923536177:AAEySIwR1PeBJdNy6sJbDHz0q8jNojVChIk'
CHAT_ID = '1062597793'



# Create a bot instance
bot = telegram.Bot(token=BOT_TOKEN)

# Scrape Nepse Index data
url2 = "https://www.nepalipaisa.com/Indices.aspx"
html2 = requests.get(url2).content
df_list2 = pd.read_html(html2)
y = np.array(df_list2[1]["Nepse Index Value"])
x = np.linspace(1, 57, len(y)).reshape(-1, 1)
from sklearn import linear_model
reg = linear_model.LinearRegression()
reg.fit(x, y)
pred = np.array(58).reshape(1, 1)
reg.predict(pred)
from datetime import date
today = date.today()
Str = date.isoformat(today)
plt.figure(figsize=(40, 25))
plt.plot(Str, reg.predict(pred), "go--")
plt.plot(df_list2[1]["Date"], df_list2[1]["Nepse Index Value"], "go--")
plt.savefig("graph.png")

# Send the image to the chat using the chat ID
with open('graph.png', 'rb') as f:
    bot.send_photo(chat_id=CHAT_ID, photo=InputFile(f))

# Scrape stock data from ShareSansar
urlstock = "https://www.sharesansar.com/market"
htmlstock = requests.get(urlstock).content
df_list_stock = pd.read_html(htmlstock)
df_stock = df_list_stock[3]

# Send the stock data to the chat using the chat ID
bot.send_message(chat_id=CHAT_ID, text='```' + '\n' + df_list_stock[-2].to_csv() + '\n'  + '```')
bot.send_message(chat_id=CHAT_ID, text='```' + '\n' + df_list_stock[-3].to_csv() + '\n'  + '```')
bot.send_message(chat_id=CHAT_ID, text='```' + '\n' + df_list_stock[-8].to_csv() + '\n'  + '```')

# Scrape share data from ShareSansar
urlshare = "https://www.sharesansar.com/?show=home"
htmlshare = requests.get(urlshare).content
df_list_share = pd.read_html(htmlshare)
df_share = df_list_share[2]

# Send the share data to the chat using the chat ID
bot.send_message(chat_id=CHAT_ID, text='```' + '\n' + df_share.to_csv() + '\n'  + '```')
bot.send_message(chat_id=CHAT_ID, text='```' + '\n' + df_list_share[6].to_csv() + '\n'  + '```')
