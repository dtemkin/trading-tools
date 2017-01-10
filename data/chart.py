'''
Created on Dec 1, 2016

@author: girlfriday
'''



import numpy

class Indicator(object):
    
    def __init__(self, data = None, **kwargs):
        self.kwargs = dict(**kwargs)
        if data is None:
            pass
        else:
            data = numpy.array(data)
            
            self.ids, self.dates, self.tstamps = data[:, 0], data[:, 3], data[:, 4]
            self.opn, self.hi, self.lo, self.cls = data[:, 5], data[:, 6], data[:, 7], data[:, 8]
            self.vol = data[:, 9]
        
        self._name = None
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, x):
        self._name = x
        
    def cci(self, n, vals = None, k = .015):
        
        self._name = "cci(%s)" % n
        typical_prices = []
        cci = []
        x = 0
        while x < len(self.ids):
            typprice = (float(self.hi[x]) + float(self.lo[x]) + float(self.cls[x])) / 3
            typical_prices.append(typprice)
            x += 1
        
        sma = self.sma(vals = typical_prices, n = n)
        meandevs = self.mean_deviation(vals = typical_prices, n = n)
        tps = typical_prices[n:]
        for i in range(len(tps)):
            cci_val = (tps[i] - sma[i]) / (k * meandevs[i])
            cci.append(cci_val)
        return cci
    
    def mean_deviation(self, n, vals = None):
        self._name = "meandev(%s)" % n
        if vals != None:
            v = vals
        else:
            v = [float(x) for x in self.cls]
        
        x = 0
        meandevs = []
        while x + n < len(v):
            mu = numpy.mean(v[x:x + n])

            dev = abs(v[x + n] - mu)
            meandevs.append(dev)
            x += 1

                
        meandevs = [sum(meandevs[i:i + n]) / n for i in range(0, len(meandevs))]
        return meandevs        
        
                    
    def rsi(self, n):
        self._name = "rsi(%s)" % n
        i = 0
        ups = []
        dns = []
        while i + 1 <= len(self.ids):
            
            chg = self.cls[i + 1] - self.cls[i]
            if chg > 0:
                ups.append(chg)
            elif chg <= 0:
                dns.append(chg)
            i += 1
        first_avggain = numpy.mean(ups[:n])
        first_avgloss = numpy.mean(dns[:n])
        if first_avgloss == 0:
            first_RSI = 100

        else:
            first_RS = first_avggain / first_avgloss
            first_RSI = 100 - (100 / (1 + first_RS))
        
        rsi = [first_RSI]
            
        for x in range(n - 1, len(self.ids) - n):
            avggain = ((ups[x - 1] * n - 1) + ups[x]) / n
            avgloss = ((dns[x - 1] * n - 1) + dns[x]) / n
            if avgloss == 0:
                RSIval = 100
            else:
                r = avggain / avgloss
                RSIval = 100 - (100 / (1 + r))
            
            rsi.append(RSIval)
            
        return rsi 
        
    def sma(self, n, vals = None):
        self._name = "sma(%s)" % n
        wts = numpy.repeat(1.0, n) / n
        smas = []
        
        if vals == None:
            v = self.cls
        
        else:
            v = vals
        x = 0
        while x < len(v) - n:
            smas.append(numpy.mean(v[x:x + n]))
            x += 1
        
        return smas
    
    def ema(self, n, vals = None):
        if vals is None:
            v = self.cls
        else:
            v = vals
        self._name = "ema(%s)" % n
        alpha = (2 / (n + 1))
        ema = [self.sma(n)]
        i = 0
        while i <= len(1, self.ids):
            ema.append((v[i] - ema[i - 1]) * alpha + ema[i - 1])
            i += 1
        return ema
    
        
    def wma(self, n):
        self._name = "wma(%s)" % n
        
        
    def macd(self, nslow, nfast, nsignal, vals = None):
        self._name = "macd(%s, %s, %s)" % (nslow, nfast, nsignal)
        if vals is None:
            emaslow, emafast, emasignal = self.ema(nslow), self.ema(nfast), self.ema(nsignal)
        else:
            v = vals
            emaslow = self.ema(v, nslow)
            emafast = self.ema(v, nfast)
            emasignal = self.ema(v, nsignal)
            
        
    def donchian_chnl(self, n):
        self._name = "Donchian Channel (%s)" % n
        
        i = 0
        donch = []
        while i < n - 1:
            donch.append(0)
            i += 1
        j = 0
        
        while j + n - 1 < len(v):
            dc = max(self.hi[j:j + n - 1]) - min(self.lo[j:j + n - 1])
            donch.append(dc)
            j += 1
        
        return donch
    
    def ulceridx(self, n):
        self._name = "Ulcer Index (%s)" % n

    def adl(self, n):
        self._name = "Accumulation/Distribution Line (%s)" % n
    
    def chaikin_osc(self, n):
        self._name = "Chaikin Oscillator (%s)" % n
    
    def mfidx(self, n):
        self._name = "Chaikin Money Flow Index (%s)" % n
    def stochastic_rsi(self, fastK, slowK, fastD):
        
        self._name = "Stochastic RSI (%s, %s, %s)" % (fastK, slowK, fastD)
        
    def stochD(self, n):
        self._name = "Stochastic Oscillator %sK (%s)" % (u"\u0025", n)
    
    def stochK(self, n):
        self._name = "Stochastic Oscillator  %sD (%s)" % (u"\u0025", n)
        return [((self.cls[i] - self.lo[i]) / (self.hi[i] - self.lo[i])) for i in range(n, len(self.ids))]
        
    def onbalVol(self, n):
        self._name = "On-Balance Volume (%s)" % n
    
    def force_idx(self, n):
        self._name = "Force Index (%s)" % n
    
    def rbar(self, n):
        self._name = "Rbar^2 Index (%s)" % n
        
    def median(self, n = None, typ = "expanding"):
        if typ == "expanding" and n is None:
            self._name = "Median [Expanding]"
        elif typ == "rolling" and n is not None:
            self._name = "Median [Rolling] (%s)" % n
        else:
            print("Error: Invalid Args.")
            print("If 'typ' = 'rolling', 'n' != None")
            print("If 'typ' = 'expanding', 'n' == None")
    
    def coefficient_variation(self, n, typ):
        pass
    

    
        
from math import pi
from bokeh.plotting import figure, show, output_file
import pandas as pd


class Plot(Indicator):
    
    def __init__(self, price_data, preferred_browser = "Chrome"):
        indic = Indicator(price_data)
        df = pd.DataFrame(price_data[1:], index = price_data[1:, 0], columns = price_data[0])
        self.df = df
        print(df)
        self.dt = df["dt"]
        self.opn, self.hi, self.lo, self.cls = df["opn"], df["hi"], df["lo"], df["cls"]
        self.vol = df["vol"]
        self.midpts = (self.opn + self.cls) / 2
        self.rng = abs(self.cls - self.opn)
        
        
    def _dataCalcs(self):
        pass
            
                
    def _setFlags(self):   
        pass
      
    
    def addIndicator(self, data, name, pos = "below"):
        pass
        
    def candlestick(self):
        up = self.cls > self.opn
        dn = self.cls < self.opn
        
        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
        
        dnfull, dnempty, upfull, upempty = numpy.array(dnfull), numpy.array(dnempty), numpy.array(upfull), numpy.array(upempty)
        w = 20000
        p = figure(x_axis_type = "datetime", tools = TOOLS, plot_width = 10000, title = "%s Plot")
        p.xaxis.major_label_orientation = pi / 4
        p.grid.grid_line_alpha = 0.3
        
        
        p.segment(self.dt, self.hi, self.dt, self.lo, color = "black")
        p.rect(self.dt[up], self.midpts[up], w, self.rng[up], fill_color = "#000000", line_color = "black")
        p.rect(self.dt[dn], self.midpts[dn], w, self.rng[dn], fill_color = "#B23434", line_color = "#B23434")

        output_file("plot.html", title = "Example")
        show(p)
    
    def indicator_plot(self, vals, ub, lb):
        pass
    

    
        
        
        
        
        
        
