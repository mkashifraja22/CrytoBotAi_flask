from flask import Flask, render_template, request, make_response, request
import json
from urllib.request import urlopen
import urllib.error
import os
import time
import json
import sqlite3
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

app = Flask(__name__)
send_list = []
rank_list=[]
data_list =[]
#used to fix the date column characters and remove time
def char_len(x, fixed_n):
    '''set string x to fixed_n character, prepend with 'xxx' if short'''
    if len(x) > fixed_n:
        return x[:fixed_n]
    elif len(x) < fixed_n:
        return 'x' * (fixed_n - len(x)) + x
    return x
#-------------------------------------
def ALL(val, pageNO=None):

    send_list = []
    rowperpage = 250
    lenght=range(1,13)

    # lenght = range(pageNO if pageNO is not None else 1, int(
    #     val/rowperpage)+1 if pageNO is None else pageNO+1)
  
    for x in lenght:
        try:
            url="https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page="+str(rowperpage)+"&page="+str(x)+"&sparkline=true&price_change_percentage=7d"
            url2="https://api.coingecko.com/api/v3/coins/markets?vs_currency=btc&order=market_cap_desc&per_page="+str(rowperpage)+"&page="+str(x)+""
            json_url=urlopen(url)
            json_url2=urlopen(url2)
            data=json.loads(json_url.read())
            dK = json.loads(json_url2.read())
            n=len(data)
            print(x)
            for i in range(n):

                dKL = '%0.8f'%dK[i]['current_price'] if dK[i]['current_price'] is not None else 0
                if float(dKL)==1:
                    dKL='1.00'
                a= int(data[i]['market_cap_rank']) if data[i]['market_cap_rank'] is not None else 0
                b=data[i]['name'] if data[i]['name'] is not None else 0
                f=data[i]['symbol'].upper() if data[i]['symbol'] is not None else 0
                c= '%0.15f'%data[i]['current_price'] if data[i]['current_price'] is not None else 0
                if "." in c:
                    c = c.rstrip("0")
                if c[-1:]==".":
                    c = c+"00"
                if float(c)>=1:
                    c='%0.2f'%data[i]['current_price'] if data[i]['current_price'] is not None else 0
                d=int(data[i]['total_volume']) if data[i]['total_volume'] is not None else 0
                e='%0.3f'%data[i]['price_change_percentage_24h'] if data[i]['price_change_percentage_24h'] is not None else 0
                g=data[i]['market_cap'] if data[i]['current_price'] is not None else 0
                e1='%0.2f'%data[i]['circulating_supply'] if data[i]['circulating_supply'] is not None else 0
                g1=data[i]['ath'] if dK[i]['ath'] is not None else 0
                h1= char_len(data[i]['ath_date'], 10) if data[i]['ath_date'] is not None else 0
                k1= data[i]['atl'] if dK[i]['atl'] is not None else 0
                m1= char_len(data[i]['atl_date'], 10) if data[i]['atl_date'] is not None else 0
                f1=data[i]['max_supply'] if data[i]['max_supply'] is not None else 0
                im11=data[i]['image'] if data[i]['image'] is not None else 0
                ID = data[i]['id']
                data1={
                    'rank':a, 'btc_val':dKL, 'logo':im11,'name':b,'symbol':f,'price':c,'volume_24h':d,
                    'change_24h':e,'market_cap':g,'circulating_supply':e1,'max_supply':f1, "id":ID,
                    'ath_price':g1,'ath_date':h1,'atl_price':k1,'atl_date':m1
                }
                if a not in rank_list:
                    
                    send_list.append(data1)
                    rank_list.append(a)

                # if a.count() <= 1:
            # print('data_inserted')      
        except:
            pass
        
    print("lennnn .......",len(send_list))
    return send_list


inputed_time = time.time()
header_data = []

# send_list = []

@app.route('/')
def index():
    global send_list
    send_list=sorted(send_list, key= lambda d: d['rank'])
    list_len = len(send_list)

    global header_data
    response = []
    
    # header crypto data
    try:
        header_url = "https://api.coingecko.com/api/v3/global"
        header_json_url = urlopen(header_url)
        response = json.loads(header_json_url.read())
    except Exception as e:
        # print(e)
        pass

    # print(header_data)
    if 'data' in response:
        header_data = response

    if 'data' in header_data:
        Cryptocurrencies_data = header_data['data']['active_cryptocurrencies']
        Markets_data = header_data['data']['markets']
        MarketCap_data = "%0.f" % (header_data['data']['total_market_cap']['usd'])
        Vol_data = "%0.f" % (header_data['data']['total_volume']['usd'])
        BTCDominance_data = "%0.1f" % (header_data['data']['market_cap_percentage']['btc'])
    else:
        Cryptocurrencies_data = []
        Markets_data = []
        MarketCap_data = []
        Vol_data = []
        BTCDominance_data = []



    return render_template('mywork.html', Cryptocurrencies=Cryptocurrencies_data, Markets=Markets_data,
                           MarketCap=MarketCap_data
                           , Vol=Vol_data, BTCDominance=BTCDominance_data, data=send_list)

def loadData(ID, fromTime, toTime):
    url = "https://api.coingecko.com/api/v3/coins/"+ID+"/market_chart/range?vs_currency=usd&from="+str(fromTime)+"&to="+str(toTime)
    data = None
    # print(ID, fromTime, toTime, url)
    while data is None:
        try:
            json_url=urlopen(url)
            data=json.loads(json_url.read())
        except urllib.error.HTTPError as e:
            # print(e.code)
            if e.code==404:
                data = {"prices":[]}
                return data
            # print("--- ERROR OCCURED, RETRYING IN 5 sec ----")
            time.sleep(5)
            print("--- RETRYING ---")
            pass
    return data

@app.route("/build_data")
def builder():
    return render_template("builder.html")

@app.route("/build_data/<start>/<limit>", methods=["GET", "POST"])
def startWorking(start, limit):
    # print("--- PROGRAM STARTED ---")
    toTime = round(time.time())
    db = sqlite3.connect("test.db")
    coins = db.execute("SELECT ID, MAX(TimeValue) FROM Coin GROUP BY ID LIMIT "+start+", "+limit).fetchall()

    for coin in coins:

        ID = coin[0]
        fromTime = int(coin[1]/1000 + 1)
        # print("--- GETTING DATA FOR " + ID +" ---")
        json_response = loadData(ID, fromTime, toTime)["prices"]
        # print("--- GOING TO STORE DATA ---")
        toInsert = [ ]
        for row in json_response:
            toInsert.append( (ID, row[0], row[1], ) )

        if len(toInsert)>0:
            db.executemany("INSERT INTO Coin(ID, TimeValue, PriceValue) VALUES(?, ?, ?)", toInsert)
        db.commit()
        # print("--- SUCCESSFULLY TAKEN DATA FOR " + ID + " ---")

    # print("--- EVERYTHING IS DONE ENDING PROGRAM ---")
    db.close()
    return make_response({"output":"done"},200)



@app.route("/reload_data/<page>", methods=["GET", "POST"])
def reload_data(page):
    
    output = sorted(send_list, key=lambda d: d['rank'], reverse=False)
    print("data_reloaded",len(output))
    return make_response({"output": output, "page": page}, 200)


@app.route("/api", methods=["POST"])
def api():
    start = int(request.form["start"])
    minTime = start+86400000
    end = int(request.form["end"])
    coins = request.form.getlist("coins[]")[0:100]
    db = sqlite3.connect("test.db")
    output = db.execute("SELECT ID, printf('%.7f',MAX(PriceValue)), printf('%.7f',MIN(PriceValue)) FROM Coin WHERE ID IN ('"+"','".join(coins)+"') AND (TimeValue BETWEEN ? AND ?) GROUP BY ID HAVING MIN(TimeValue) <= ?", (start, end, minTime,)).fetchall()
    for i in range(len(output)):
        output[i] = list(output[i])
    return make_response({"output":output, "start":start, "end":end, "coins":coins},200)


def do_update():
    global send_list
    send_list = sorted(ALL(3468), key=lambda d: d['rank'])
    print("schedular list ........",len(send_list))
   


do_update()
# scheduler = BackgroundScheduler()
# scheduler.add_job(do_update, "interval", seconds=60)
# scheduler.start()
# atexit.register(lambda: scheduler.shutdown())

#@app.route("/comingsoon")
#def comingsoon():
 #   return render_template("coming_soon.html")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=4000, debug=True)

