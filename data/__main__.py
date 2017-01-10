'''
Created on Dec 4, 2016

@author: girlfriday
'''
from source.barchart import Ticks
from chart import Indicator, Plot
import csv

ticker = "ESY00"

src = Ticks(symbol="ESZ16", interval=1, sdate="2016-12-04", edate="2016-12-04", exchange="CME")
src.download()
arr = src.makeBars(nticks=100)
fields = arr[0][0]

plt = Plot(price_data=arr)
plt.candlestick()
with open("/home/girlfriday/Documents/Crockett/Ticks-20151205.csv", mode="a") as f:
    writr = csv.DictWriter(f, fieldnames=fields)
    

    for x in range(1, len(arr)):
        if len(fields) == 9:
            d = {"id": int(arr[:,0][x]), "symbol": arr[:,1][x], "src": arr[:,2][x],
                 "dt": str(arr[:,3][x]), "date": str(arr[:,4][x]), "timestamp": float(arr[:,5][x]),
                 "flag": float(arr[:,6][x]), "price": float(arr[:,7][x]),
                 "vol": float(arr[:,8][x])}
            writr.writerow(d)
        elif len(fields) == 11:
            d = {"id": int(arr[:,0][x]), "symbol": arr[:,1][x], "src": arr[:,2][x],
                 "dt": str(arr[:,3][x]), "date": str(arr[:,4][x]), "timestamp": float(arr[:,5][x]),
                 "opn": float(arr[:,6][x]), "hi": float(arr[:,7][x]), "lo": float(arr[:,8]),
                 "cls": float(arr[:,9][x]), "vol": float(arr[:,10][x])}
        
            writr.writerow(d)
    f.close()
