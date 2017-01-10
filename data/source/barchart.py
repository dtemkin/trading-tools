import os, sys
import datetime
import requests
import numpy
from time import time, sleep
from abc import ABCMeta, abstractmethod, abstractproperty

from matplotlib import pyplot as plt
from utils import getOSMods, getwd, datetools, conftools
import csv
from data import __base__
    

    

pthmark, hdf5drv, nl = getOSMods()
source = Source()


source.name = "barchart"
source.ticksurl = "https://www.barchart.com/proxies/timeseries/queryticks.ashx?"
source.intradayurl = "https://www.barchart.com/proxies/timeseries/queryminutes.ashx?"
source.dailyurl = "https://www.barchart.com/proxies/timeseries/queryeod.ashx?"
source.cfgfile = "".join([pthmark, "configs", pthmark, "barchart.conf"])


class Ticks(__base__.Meta):
    
    def __init__(self, symbol, interval, sdate, edate=datetime.datetime.today(), dateformat="%Y-%m-%d", **kwargs):
        """
        Arguments
        
        symbol : str 
            Symbol is two characters or less. Acts as a prefix.
            contract argument != 'continuous'.
        period : str
            The granularity of the data to return.
            Accepts: 'ticks', 'minutes', 'hours', 'days'
        interval: int
            The interval in which to report the data for each period. 
            (e.g. if period=minutes and interval=30, the data returned would be spaced in 30 minute intervals)
            Default interval = 1 
        sdate : str
            The earliest date to retrieve.
            If is None retrieves date from config file
            Expects Argument dateformat = "%Y-%m-%d" (e.g. 2012-01-01)
            May be limited due to api restrictions on data period
        edate : str
            The last date to include in query.
            If edate = None will default to today.
            If edate = "continue", will pull last date from config file.
            Expects Argument dateformat = "%Y-%m-%d" 
            May be limited due to api restrictions on data period
        dateformat : str
            Default = "%Y-%m-%d"
        contract : str
            Specifies the data to return depending on specified contract.
            Accepts values - 'nearest', 'continuous'
            If contract = 'nearest' will return the data for the next most recent contract until expiration and rollover progressively until edate.
            If contract = 'continuous' will overwrite symbol to "xxY00" - Note: No Volume is Reported for the Continuous Contract
            Default: contract = 'continuous'
        exchange : str
            Attempt to limit results to those reported by a particular exchange. 
            Accepts: CME, GLBX, NYMEX, CBOT, CBOTM, ICEUS, COMEX...
                     for complete list see barchart_exch.ls file in .info
            Note: This does not always seem to be reliable. #TODO
        volume : str
            Specify volume units.
            Default: volume = 'contracts'
        maxresults : int
            Specify the max number of results to return
        """

        self.urls = []
        # Length 9
        self.aggArray = numpy.array(["id","symbol", "src", "dt","date","timestamp","flag","settle","vol"]) 
        # Length 11
        self.groupedArray = numpy.array(["id","symbol","src","dt","date","timestamp","opn","hi","lo","cls","vol"])
        self.period = "ticks"
        self.baseurl = source.ticksurl
        self.symbol = symbol
        self.interval = interval
        self.dateformat = dateformat
        
        if type(edate) is str:
            self.end = datetools().str2dt(edate, dateformat)
        elif type(edate) is datetime.datetime:
            self.end = edate
        elif edate is None:
            print("Using default end date...")
            self.end = datetime.datetime.today()
        if sdate is None:
            print("Using default start date...")
            self.start = datetools().calcStart(edate, dateformat, 365)
        else:
            self.start = datetools().str2dt(sdate, dateformat)
        
        self.dates = datetools().genDates(self.start, self.end) 
        self.kwargs = dict(**kwargs)
        
    def download(self):
        x = 0
        arrs =[]
        for j in range(len(self.dates)):
            args = {"symbol":self.symbol, "interval":self.interval, "start":datetools().dt2str(self.dates[j]), **self.kwargs}
            try:
                print("Downloading Tick Data for %s -- %s" % (self.symbol, self.dates[j]))
                r = requests.get(self.baseurl, params=args)
            except Exception as err:
                print(err + "\nSkipping...")
                pass
            else:
                sleep(1)
                raw = r.text.replace("\r", "")
                rows = raw.split("\n")
                
                for i in range(len(rows)-1):
                    if len(rows[i]) <= 1:
                        pass
                    else:
                        x += 1
                    
                        row= rows[i].split(",")
                   
                        dt = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
                        arr = [x, self.symbol, source.name, dt, datetime.date(dt.year, dt.month, dt.day).strftime("%Y%m%d"), dt.time().strftime("%H:%M:%S.%f"), str(row[2]), float(row[3]), int(row[4])]
                        arrs.append(arr)
        self.aggArray = numpy.vstack((self.aggArray, arrs))
                    
        return self.aggArray    
                            
                        
                    
    def makeBars(self, nticks=60):
        groupedArray = numpy.array(["id","symbol","src","dt","date","timestamp","opn","hi","lo","cls","vol"])
        bars = []
        IDs = self.aggArray[:,0]
        print("Building Bars")

        rawbars = [self.aggArray[:,7][i:i+nticks] for i in range(1, len(IDs), nticks)]
        volbars = [self.aggArray[:,8][i:i+nticks] for i in range(1, len(IDs), nticks)]
        timebars = [self.aggArray[:,5][i:i+nticks] for i in range(1, len(IDs), nticks)]
        datebars = [self.aggArray[:,4][i:i+nticks] for i in range(1, len(IDs), nticks)]
        dtbars = [self.aggArray[:,3][i:i+nticks] for i in range(1, len(IDs), nticks)]
        
        for b in range(len(rawbars)):
            bar = [b, self.symbol, source.name, dtbars[b][0], datebars[b][0], timebars[b][0], rawbars[b][0], max(rawbars[b]), min(rawbars[b]), rawbars[b][-1], sum(volbars[b])]
            bars.append(bar)
    
        groupedArray = numpy.vstack((groupedArray, bars))
        return groupedArray
    
    def sample(self, nrows, select="random"):
        if nrows >= len(self.databars):
            print("Too many nrows requested. Only %d bars found." % len(self.databars))
        else:
            print("Selecting Sample")
            if select == "top":
                print(self.databars[:nrows])
            elif select == "end":
                print(self.databars[len(self.databars)-(nrows+1):len(self.databars)-1])
            elif select == "random":
                selected = numpy.random.choice([i for i in range(len(self.databars))], replace=False, size=nrows)
                print("Showing %s of %s data rows" % (nrows, len(self.databars)))
                for s in selected:
                    print(self.databars[s])
    
    def plot(self, nticks, sym):
        print("Plotting Candlestick Chart")
        plt.plot(self.databars[:,0], self.databars[:,6])
        plt.xlabel("Number of 'Bars'")
        plt.ylabel("Close Price")
        plt.title("%s - %s Ticks Data" % (sym, nticks) )
        plt.show()

class Minutely(__base__.Meta):
    
    def __init__(self, symbol, interval, sdate, dateformat="%Y-%m-%d", volume_units="contracts", order="asc", **kwargs):
        """
        Arguments
        
        symbol : str 
            Exchange listed symbol
        interval: int
            The interval in which to report the data for each period. 
            (e.g. if period=minutes and interval=30, the data returned would be spaced in 30 minute intervals)
            Default interval = 1 
        sdate : str
            The earliest date to retrieve.
            If is None retrieves date from config file
            Expects Argument dateformat = "%Y-%m-%d" (e.g. 2012-01-01)
            May be limited due to api restrictions on data period
        edate : str
            The last date to include in query.
            If edate = None will default to today.
            If edate = "continue", will pull last date from config file.
            Expects Argument dateformat = "%Y-%m-%d" 
            May be limited due to api restrictions on data period
        dateformat : str
            Default = "%Y-%m-%d"
        exchange : str
            Attempt to limit results to those reported by a particular exchange. 
            Accepts: CME, GLBX, NYMEX, CBOT, CBOTM, ICEUS, COMEX...
                     for complete list see barchart_exch.ls file in .info
            Note: This does not always seem to be reliable. #TODO
        volume : str
            Specify volume units.
            Default: volume = 'contracts'
        maxresults : int
            Specify the max number of results to return
        """
        self.datadict = {"id":[], "pricedata":
                         {"symbol":[], "dt":[], "date":[],"timestamp":[],
                          "flag":[],"prices":[],"vol":[]}}
        self.databars = []
    
        self.period = "minutes"
        self.baseurl = source.intradayurl
        self.symbol = symbol
        self.interval = interval
        self.kwargs = dict(**kwargs)
        self.dateformat = "%Y-%m-%d"
        self.rawbars = []
        if sdate is None:
            print("Using Default Start Date...")
            self.start = datetools().str2dt("2012-01-03", dateformat)
        elif type(sdate) is str:
            self.start = datetools().str2dt(sdate, dateformat)
        else:
            self.start =""
            
        if 'edate' in self.kwargs.keys():
            edate = self.kwargs['edate']
            if type(edate) is str:
                self.end = datetools().str2dt(edate, dateformat)
            elif type(edate) is datetime.datetime:
                self.end = datetools().dt2str(edate)
            elif edate is None:
                print("Using Default...")
                self.end = ""
        else:
            self.end = ""
        self.volume = volume_units
        self.order = order
        
        
    def download(self):
        args = {"symbol":self.symbol, "interval":self.interval,
                "start":datetools().dt2str(self.start),"end":self.end,
                "volume":self.volume, "order":self.order}
    
        try:
            r = requests.get(self.baseurl, params={**args, **self.kwargs})
        except Exception as err:
            print("Error: %s" % err)
            print("Attempting to skip...")
            pass
        else:
            sleep(1)
            raw = r.text.replace("\r", "")
            rows = raw.split("\n")
            for i in range(len(rows)-1):
                self.datadict["id"].append(i)
                
                row= rows[i].split(",")
                if len(row) <= 1:
                    pass
                else:
                    prcdata= self.datadict["pricedata"]
                    
                    date, timestamp = row[0].split(" ")
                    
                    day = int(row[1])
                    opn, hi = float(row[2]), float(row[3])
                    lo, cls = float(row[4]), float(row[5])
                    prcdata["dt"].append(row[0])
                    prcdata["date"].append(date)
                    prcdata["timestamp"].append(timestamp)
                    prcdata["prices"].append([opn, hi, lo, cls])
                    prcdata["vol"].append(int(row[6]))
                    
        
                    self.databars.append((i, self.symbol, source.name, datetools().dt2str(datetools().str2dt(date, self.dateformat)), timestamp, opn, hi, lo, cls, int(row[6])))  
                    
    
    def makeBars(self):
        return numpy.array(self.databars)
    
    def sample(self, nrows, select="random"):
        prcdata = self.datadict["pricedata"]["prices"]
        if nrows >= len(self.datadict["pricedata"]["prices"]):
            print("Too many nrows requested. Only %d bars found." % len(self.databars))
        else:
            print("Selecting Sample")
            if select == "top":
                print(prcdata[:nrows])
            elif select == "end":
                print(self.databars[len(self.databars)-(nrows+1):len(self.databars)-1])
            elif select == "random":
                selected = numpy.random.choice([i for i in range(len(self.databars))], replace=False, size=nrows)
                print("Showing %s of %s data rows" % (nrows, len(self.databars)))
                for s in selected:
                    print(self.databars[s])
    


            
### TODO      
# class Morningstar(Source):
#     pass
# 
# class Yahoo(Source):
#     pass
# 
# class Google(Source):
#     pass     
#     




