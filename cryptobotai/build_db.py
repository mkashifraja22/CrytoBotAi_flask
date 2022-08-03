import os
import time
import json
import sqlite3
from urllib.request import urlopen

def loadData(ID, fromTime, toTime):
	url = "https://api.coingecko.com/api/v3/coins/"+ID+"/market_chart/range?vs_currency=usd&from="+str(fromTime)+"&to="+str(toTime)
	data = None
	print(ID, fromTime, toTime)
	while data is None:
		try:
			json_url=urlopen(url)
			data=json.loads(json_url.read())
		except:
			print("--- ERROR OCCURED, RETRYING IN 5 sec ----")
			time.sleep(10)
			print("--- RETRYING ---")
			pass
	return data

def startWorking():

	print("--- PROGRAM STARTED ---")
	toTime = round(time.time())
	db = sqlite3.connect("test.db")
	coins = db.execute("SELECT ID, MAX(TimeValue) FROM Coin GROUP BY ID").fetchall()
	
	for coin in coins:

		ID = coin[0]
		fromTime = int(coin[1]/1000 + 1)
		print("--- GETTING DATA FOR " + ID +" ---")
		json_response = loadData(ID, fromTime, toTime)["prices"]
		print("--- GOING TO STORE DATA ---")
		toInsert = [ ]
		for row in json_response:
			toInsert.append( (ID, row[0], row[1], ) )
		
		if len(toInsert)>0:
			db.executemany("INSERT INTO Coin(ID, TimeValue, PriceValue) VALUES(?, ?, ?)", toInsert)
		db.commit()		
		print("--- SUCCESSFULLY TAKEN DATA FOR " + ID + " ---")

	print("--- EVERYTHING IS DONE ENDING PROGRAM ---")
	db.close()

startWorking()