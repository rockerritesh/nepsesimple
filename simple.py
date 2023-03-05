#!/usr/bin/env python
# coding: utf-8
# Open the file in read mode
with open("html.txt", "r") as f:
    # Read the contents of the file
    asadas = f.read()

# print(asadas)

import requests
import pandas as pd
import numpy as np

# import openpyxl
import matplotlib.pyplot as plt
import bs4
import html5lib

# ----MY----
#BOT_TOKEN = ""
#CHAT_ID = ""

import telegram
from telegram import InputFile

# Create a bot instance
#bot = telegram.Bot(token=BOT_TOKEN)
# In[143]:


url2 = "https://www.nepalipaisa.com/Indices.aspx"
html2 = requests.get(url2).content
df_list2 = pd.read_html(html2)


y = np.array(df_list2[1]["Nepse Index Value"])
y.shape


x = np.linspace(1, 57, len(y)).reshape(-1, 1)
x.shape

# In[151]:


from sklearn import linear_model

reg = linear_model.LinearRegression()
reg.fit(x, y)
pred = np.array(58).reshape(1, 1)
reg.predict(pred)


from datetime import date

today = date.today()
# today
Str = date.isoformat(today)
plt.figure(figsize=(40, 25))
# plt.plot(df_list2[1]['Absolute Change'])
# plt.plot(df_list2[1]['Percent Change'])
plt.plot(Str, reg.predict(pred), "go--")
plt.plot(df_list2[1]["Date"], df_list2[1]["Nepse Index Value"], "go--")
plt.savefig("graph.png")


# Send the image to the chat using the chat ID
#with open("graph.png", "rb") as f:
#    bot.send_photo(chat_id=CHAT_ID, photo=InputFile(f))

# FOR STOCK

urlstock = "https://www.sharesansar.com/market"
htmlstock = requests.get(urlstock).content
df_list_stock = pd.read_html(htmlstock)

df_stock = df_list_stock[3]
df_stock.to_csv("stock.csv")
df_stock.to_html("stock.html")


# In[157]:


df_list_stock[-2].to_html("toptransactions.html")

# Send a message to the chat using the chat ID
#bot.send_message(
#    chat_id=CHAT_ID, text="```" + "\n" + df_list_stock[-2].to_csv() + "\n" + "```"
#)

df_list_stock[-3].to_html("topvolume.html")

# Send a message to the chat using the chat ID
#bot.send_message(
#    chat_id=CHAT_ID, text="```" + "\n" + df_list_stock[-3].to_csv() + "\n" + "```"
#)

df_list_stock[-7].to_html("gold.html")
df_list_stock[-8].to_html("compare.html")

# Send a message to the chat using the chat ID
#bot.send_message(
#    chat_id=CHAT_ID, text="```" + "\n" + df_list_stock[-8].to_csv() + "\n" + "```"
#)

index = df_list_stock[-12].to_html()
urlshare = "https://www.sharesansar.com/?show=home"
htmlshare = requests.get(urlshare).content
df_list_share = pd.read_html(htmlshare)
df_share = df_list_share[2]
df_share.to_csv("ipo.csv")

# Send a message to the chat using the chat ID
#bot.send_message(chat_id=CHAT_ID, text="```" + "\n" + df_share.to_csv() + "\n" + "```")

df_share.to_html("ipo.html")
df_list_share[1].to_html("bonous.html")
df_list_share[4].to_html("newsofbank.html")
df_list_share[5].to_html("stock.html")
df_list_share[6].to_html("gradeofcompany.html")

# Send a message to the chat using the chat ID
#bot.send_message(
#    chat_id=CHAT_ID, text="```" + "\n" + df_list_share[6].to_csv() + "\n" + "```"
#)

df_list_share[7].to_html("companymerged.html")
df_list_share[0].to_html("bookclosure.html")
"""# new way direct from nepalstock.com

nepse = requests.get("http://nepalstock.com")
soup = bs4.BeautifulSoup(nepse.text, "html5lib")
category = soup.find_all(class_="panel-body")

html = asadas + str(category[3]) + "</body> </html>"
with open("marketsummary.html", "w") as output:
    output.write(html)

html = asadas + str(category[2]) + "</body> </html>"
with open("marketdata.html", "w") as output:
    output.write(html)

html = asadas + str(category[4]) + "</body> </html>"
with open("todayindex.html", "w") as output:
    output.write(html)"""

# json file nepssimpleeapi
df = pd.read_html("https://www.sharesansar.com/today-share-price")
df = df[-1].T
# Send a message to the chat using the chat ID
# bot.send_message(chat_id=CHAT_ID, text=df.to_csv())

df.to_json("nepsesimple.json")
html = df.T.to_html()
html = asadas + index + html + "</body> </html>"
with open("index.html", "w") as output:
    output.write(html)
