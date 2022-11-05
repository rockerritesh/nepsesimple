#!/usr/bin/env python
# coding: utf-8

# In[141]:


asadas = """<html><head>NEPSE SIMPLE</head><header>
		
	<!-- Top header menu containing
		logo and Navigation bar -->
	<div id="top-header">
			
		<!-- Logo -->
		<div id="logo">
			<a href="https://sumityadav.com.np">
			<img src= https://rockerritesh.github.io/nepsesimple/android-chrome-192x192.png>	
			</a>	
		</div>
				
		<!-- Navigation Menu -->
		<nav>
			<ul>
				<li class="active"><a href="https://rockerritesh.github.io/nepsesimple/index">Home</a></li>
				<li><a href="https://rockerritesh.github.io/nepsesimple/each_company">Today Summary</a></li> 
				<li><a href="https://rockerritesh.github.io/nepsesimple/marketsummary">Summary</a></li>
				<li><a href="https://rockerritesh.github.io/nepsesimple/marketdata">Top Value Data</a></li>
				<li><a href="https://rockerritesh.github.io/nepsesimple/ipo">IPO</a></li>
				<li><a href="https://rockerritesh.github.io/nepsesimple/todayindex">Indices</a></li>
				
				<li><a href="https://rockerritesh.github.io/nepsesimple/topvolume">Today TOP VOLUME</a></li> 
				<li><a href="https://rockerritesh.github.io/nepsesimple/toptransactions">Top Transactions</a></li>
				<li><a href="https://rockerritesh.github.io/nepsesimple/gradeofcompany">Grade Of Company</a></li>
				<li><a href="https://rockerritesh.github.io/nepsesimple/compare">Compare Company</a></li>
				
        <li><a href="https://rockerritesh.github.io/nepsesimple/each_company">Each Company</a></li>
				<p dir="auto"><a href="https://github.com/rockerritesh/nepsesimple/actions/workflows/update.yml"><img src="https://github.com/rockerritesh/nepsesimple/actions/workflows/update.yml/badge.svg" alt="Update file(s)" style="max-width: 100%;"></a></p>
			</ul>
		</nav>
	</div>
  <p><img class="lazyautosizes lazyloaded" src="https://github.com/rockerritesh/nepsesimple/raw/main/graph.png" data-src="https://github.com/rockerritesh/nepsesimple/raw/main/graph.png" data-srcset="https://github.com/rockerritesh/nepsesimple/raw/main/graph.png, https://github.com/rockerritesh/nepsesimple/raw/main/graph.png 1.5x, https://github.com/rockerritesh/nepsesimple/raw/main/graph.png 2x" data-sizes="auto" alt="https://github.com/rockerritesh/nepsesimple/raw/main/graph.png" title="Graph" sizes="800px" srcset="https://github.com/rockerritesh/nepsesimple/raw/main/graph.png, https://github.com/rockerritesh/nepsesimple/raw/main/graph.png 1.5x, https://github.com/rockerritesh/nepsesimple/raw/main/graph.png 2x"></p>
	<!-- Image menu in Header to contain an Image and
		a sample text over that image -->
	<div id="header-image-menu">

	</div>
</header>

<script button.addEventListener('click', () => {
  document.body.classList.toggle('dark')
  localStorage.setItem(
    'theme',
    document.body.classList.contains('dark') ? 'dark' : 'light'
  )
})
if (localStorage.getItem('theme') === 'dark') {
  document.body.classList.add('dark')
}></script>
     
    <style>
        body{
        padding:10% 3% 10% 3%;
        text-align:center;
        }
        img{
            height:140px;
                width:140px;
        }
        h1{
        color: #32a852;
        }
        .mode {
            float:right;
        }
        .change {
            cursor: pointer;
            border: 1px solid #555;
            border-radius: 40%;
            width: 20px;
            text-align: center;
            padding: 5px;
            margin-left: 8px;
        }
        .dark{
            background-color: #000;
            color: #fff;
        }
	 
    </style>

<body>


"""


# In[142]:


import requests
import pandas as pd
import numpy as np

# import openpyxl
import matplotlib.pyplot as plt
import bs4
import html5lib


# In[143]:


url2 = "https://www.nepalipaisa.com/Indices.aspx"
html2 = requests.get(url2).content
df_list2 = pd.read_html(html2)


# In[144]:


# df_list2[0]


# In[145]:


# df_list2[1][1:5]


# In[146]:


# df_list2[1].shape


# In[147]:


# df_list2[1]['Date'][1:6]


# In[148]:


# plt.figure(figsize=(40, 25))
# plt.plot(df_list2[1]['Absolute Change'])
# plt.plot(df_list2[1]['Percent Change'])
# plt.plot( df_list2[1]['Date'],df_list2[1]['Nepse Index Value'], "go--")


# In[149]:


x = np.linspace(1, 57, len(y)).reshape(-1, 1)
x.shape


# In[150]:


y = np.array(df_list2[1]["Nepse Index Value"])
y.shape


# In[151]:


from sklearn import linear_model

reg = linear_model.LinearRegression()
reg.fit(x, y)


# In[ ]:


# In[152]:


pred = np.array(58).reshape(1, 1)


# In[153]:


reg.predict(pred)


# In[154]:


from datetime import date

today = date.today()
# today
Str = date.isoformat(today)
# Str


# In[155]:


plt.figure(figsize=(40, 25))
# plt.plot(df_list2[1]['Absolute Change'])
# plt.plot(df_list2[1]['Percent Change'])
plt.plot(Str, reg.predict(pred), "go--")
plt.plot(df_list2[1]["Date"], df_list2[1]["Nepse Index Value"], "go--")
plt.savefig("graph.png")


# In[156]:


# FOR STOCK

urlstock = "https://www.sharesansar.com/market"
htmlstock = requests.get(urlstock).content
df_list_stock = pd.read_html(htmlstock)

df_stock = df_list_stock[3]
df_stock.to_csv("stock.csv")
df_stock.to_html("stock.html")


# In[157]:


df_list_stock[-2].to_html("toptransactions.html")


# In[158]:


df_list_stock[-3].to_html("topvolume.html")


# In[159]:


# df_list_stock[-4]


# In[160]:


# df_list_stock[-5]


# In[161]:


# df_list_stock[-6]


# In[162]:


df_list_stock[-7].to_html("gold.html")


# In[163]:


df_list_stock[-8].to_html("compare.html")


# In[164]:


# df_list_stock[-9]


# In[165]:


# df_list_stock[-10]


# In[166]:


# df_list_stock[-11]


# In[167]:


index = df_list_stock[-12].to_html()


# In[168]:


urlshare = "https://www.sharesansar.com/?show=home"
htmlshare = requests.get(urlshare).content
df_list_share = pd.read_html(htmlshare)

df_share = df_list_share[2]
df_share.to_csv("ipo.csv")
df_share.to_html("ipo.html")


# In[169]:


df_list_share[1].to_html("bonous.html")


# In[170]:


# df_list_share[3]


# In[171]:


df_list_share[4].to_html("newsofbank.html")


# In[172]:


df_list_share[5].to_html("stock.html")


# In[173]:


df_list_share[6].to_html("gradeofcompany.html")


# In[174]:


df_list_share[7].to_html("companymerged.html")


# In[175]:


df_list_share[0].to_html("bookclosure.html")


# In[176]:


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


# In[177]:


# json file nepssimpleeapi
df = pd.read_html("http://www.nepalstock.com/todaysprice/export")
df = df[-1].T
df.to_json("nepsesimple.json")


# In[178]:


# df.T


# In[179]:


html = df.T.to_html()
html = asadas + index + html + "</body> </html>"
with open("index.html", "w") as output:
    output.write(html)


# In[ ]:
