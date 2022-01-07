from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find("table", attrs={"class":"table table-striped table-hover table-hover-solid-row table-simple history-data"})
row = table.find_all("td")

row_length = len(row[2::4])

temp = [] #initiating a list 

for i in range(0, row_length):

    #get tanggal
    tanggal = row[::4][i].text
    
    #get harga harian
    harga_harian = row[2::4][i].text
    harga_harian = harga_harian.strip() #to remove excess white space
    
    temp.append((tanggal,harga_harian))  

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('tanggal','harga_harian'))

#insert data wrangling here
df['harga_harian'] = df['harga_harian'].str.replace(" IDR","")
df['harga_harian'] = df['harga_harian'].str.replace(",","")
df['harga_harian'] = df['harga_harian'].astype('float')
df['tanggal'] = df['tanggal'].astype('datetime64')
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.options.display.float_format = '{:,}'.format
df = df.set_index('tanggal')
#end of data wrangling 

#Extra Challenge
df1 = df.reset_index()
df1['hari'] = df1['tanggal'].dt.day_name()
dfhari = df1.groupby('hari').mean().sort_values('harga_harian', ascending=False)
wday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
dfhari.index = pd.CategoricalIndex(
    data = dfhari.index, # list data yang ingin diubah urutannya
    categories = wday, # list data urutan yang benar
    ordered = True)
dfhari1 = dfhari.sort_index()

@app.route("/")
def index(): 
	
	card_data = f'{df["harga_harian"].mean().round(2)}' #be careful with the " and ' 

	# generate plot 1
	ax = df.plot(figsize = (12,7)) 
	
	# Rendering plot 1
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# generate plot 2
	ay = dfhari1.plot(figsize = (12,7))

	# Rendering plot 2
	# Do not change this
	figfile2 = BytesIO()
	plt.savefig(figfile2, format='png', transparent=True)
	figfile2.seek(0)
	figdata_png2 = base64.b64encode(figfile2.getvalue())
	plot_result2 = str(figdata_png2)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
		plot_result2=plot_result2
		)


if __name__ == "__main__": 
    app.run(debug=True)