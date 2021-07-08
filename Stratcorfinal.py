import backtrader as bt
import datetime
import talib 
import math
#import ta
import pandas as pd
import scipy.stats as stats
import numpy as np

class Strat(bt.Strategy):
    def __init__(self):
         #Keep a reference to the "close" line in the data[0] dataseries
         file = open("MyFile.txt", "r") 
         s=file.read()
         self.data.close = self.datas[0].close
         self.data.high=self.datas[0].high
         self.data.low=self.datas[0].low
         self.data.volume=self.datas[0].volume
         self.s=s
         self.list=[]
         
         if 'rsi' in s.lower():
             self.rsi=bt.talib.RSI(self.data.close, timeperiod=14)
             self.list.append('rsi')
         
         if 'macd' in s.lower():
             self.macd = bt.talib.MACD(self.data.close, fastperiod=12, slowperiod=26, signalperiod=9)
             self.list.append('macd')

         if 'wr' in s.lower():
             self.wr=bt.talib.WILLR(self.data.high,self.data.low,self.data.close, timeperiod=14)
             self.list.append('wr')

         if 'ema' in s.lower():
             self.ema=bt.talib.EMA(self.data.close, timeperiod=30)
             self.list.append('ema')

             
         if 'mfi' in s.lower():
             self.mfi=bt.talib.MFI(self.data.high ,self.data.low,self.data.close, self.data.volume,timeperiod=14)
             self.list.append('mfi')
             
         if 'mavg' in s.lower():
             self.bbandup=bt.talib.BBANDS(self.data.close,timeperiod=20).upperband
             self.bbandlow=bt.talib.BBANDS(self.data.close,timeperiod=20).lowerband
             self.list.append('bband')
             
         if 'adx' in s.lower():
             self.adx=bt.talib.ADX(self.data.high,self.data.low,self.data.close, timeperiod=14)
             self.list.append('adx')
             
         if 'stoch' in s.lower():
             self.stoch=bt.talib.STOCH(self.data.high,self.data.low,self.data.close).slowk
             self.list.append('stoch')
             
         if 'trix' in s.lower():
             self.trix=bt.talib.TRIX(self.data, timeperiod=5)
             self.list.append('trix')
             
         if 'ad' in s.lower():
             self.ad=bt.talib.AD(self.data.high ,self.data.low,self.data.close, self.data.volume)
             self.list.append('ad')

         if 'sma' in s.lower():
             self.sma1=bt.talib.SMA(self.data, timeperiod=5)
             self.sma2=bt.talib.SMA(self.data, timeperiod=20)
             self.list.append('sma1')
         

    
    def log(self, txt, dt=None):     
        dt = dt or self.datas[0].datetime.date(0)     
        print('%s, %s' % (dt.isoformat(), txt)) #Print date and close
        

    def next(self):
        p=self.s.split(',')
        lit=[]
        num=0
        self.log('Close, %.2f' % self.data.close[0]) 
        if 'rsi' in self.list:
           # if not self.position:
                if self.rsi[-1]>30 and self.rsi[0] <= 30 :
                    self.log('BUY CREATE RSI, %.2f' % self.data.close[0])
                    self.buy()
                    num=num+1
                    lit.append((p[p.index('rsi')+1],'buy'))

           # else:
                if self.rsi[-1]<70 and self.rsi[0] >= 70:
                    self.log('SELL CREATE RSI, %.2f' % self.data.close[0])
                    self.sell()
                    num=num+1
                    lit.append((p[p.index('rsi')+1],'sell'))
                    
                
        if 'macd' in self.list:
           # if not self.position:
                if ((self.macd.macd[-3]<0 and self.macd.macd[-2]>=0 and self.macd.macd[-1]>0 and self.macd.macd[0]>0) 
                   or (self.macd.macd[-1]<self.macd.macdsignal[-1] and self.macd.macd[0]>=self.macd.macdsignal[0])):
                      self.log('BUY CREATE MACD, %.2f' % self.data.close[0])
                      self.buy()
                      num=num+1
                      try:
                          lit.append((p[p.index('MACD_12_26')+1],'buy'))
                      except:
                          lit.append((p[p.index('Macd_signal')+1],'buy'))
           # else:
                if ((self.macd.macd[-3]>0 and self.macd.macd[-2]<=0 and self.macd.macd[-1]<0 and self.macd.macd[0]<0)
                   or (self.macd.macd[-1]>self.macd.macdsignal[-1] and self.macd.macd[0]<=self.macd.macdsignal[0])):
                    self.log('SELL CREATE MACD, %.2f' % self.data.close[0])
                    self.sell()
                    num=num+1
                    try:
                          lit.append((p[p.index('MACD_12_26')+1],'sell'))
                    except:
                          lit.append((p[p.index('Macd_signal')+1],'sell'))
                
        
        if 'mfi' in self.list:
           # if not self.position:
                if (self.mfi[-1]<80 and self.mfi[0]>=80):
                    self.log('SELL CREATE MFI, %.2f' % self.data.close[0])
                    self.sell()
                    num=num+1
                    lit.append((p[p.index('mfi_14')+1],'sell'))
           # else:
                if (self.mfi[-1]>20 and self.mfi[0]<=20 ):
                    self.log('BUY CREATE MFI , %.2f' % self.data.close[0])
                    self.buy()
                    num=num+1
                    lit.append((p[p.index('mfi_14')+1],'buy'))
                
        
        if 'sma1' in self.list:
           # if not self.position:
                if (self.sma1[-2]<self.sma2[-2] and self.sma1[0]>self.sma2[0]):
                    self.log('BUY CREATE SMA, %.2f' % self.data.close[0])
                    self.buy()
                    num=num+1
                    try:
                        lit.append((p[p.index('Close SMA50')+1],'buy'))
                    except:
                        lit.append((p[p.index('Close SMA200')+1],'buy'))

                        
                        
           # else:
                if (self.sma1[-2]>self.sma2[-2] and self.sma1[0]<self.sma2[0]):
                    self.log('SELL CREATE SMA, %.2f' % self.data.close[0])
                    self.sell()
                    num=num+1
                    try:
                        lit.append((p[p.index('Close SMA50')+1],'sell'))
                    except:
                        lit.append((p[p.index('Close SMA200')+1],'sell'))
        if 'wr' in self.list:
           # if not self.position:
                if (self.wr[-1]<-20 and self.wr[0]>=-20):
                    self.log('SELL CREATE WR, %.2f' % self.data.close[0])
                    self.sell()
                    num=num+1
                    lit.append((p[p.index('wr')+1],'sell'))
            #else:
                if (self.wr[-1]>-80 and self.wr[0]<=-80 ):
                    self.log('BUY CREATE WR, %.2f' % self.data.close[0])
                    self.buy()
                    num=num+1
                    lit.append((p[p.index('wr')+1],'buy'))
        if 'stoch' in self.list:
            #if not self.position:
                if (self.stoch[-1]<80 and self.stoch[0]>=80):
                    self.log('SELL CREATE STOCH, %.2f' % self.data.close[0])
                    self.sell()
                    num=num+1
                    lit.append((p[p.index('stoch_k')+1],'sell'))
           # else:
                if (self.stoch[-1]>20 and self.stoch[0]<=20 ):
                    self.log('BUY CREATE STOCH, %.2f' % self.data.close[0])
                    self.buy()
                    num=num+1
                    lit.append((p[p.index('stoch_k')+1],'buy'))
        if 'trix' in self.list:
            #if not self.position:
                if (self.trix[-1]<0 and self.trix[0]>=0):
                    self.log('SELL CREATE TRIX, %.2f' % self.data.close[0])
                    self.sell()
                    num=num+1
                    lit.append((p[p.index('trix_15')+1],'sell'))
            #else:
                if (self.trix[-1]>0 and self.trix[0]<=0 ):
                    self.log('BUY CREATE TRIX, %.2f' % self.data.close[0])
                    self.buy()
                    num=num+1
                    lit.append((p[p.index('trix_15')+1],'buy'))
        if 'adx' in self.list:
            #if not self.position:
                if (self.adx[-3]<25 and self.adx[-2]>=25 and self.adx[-1]>25 and self.adx[0]>25):
                    self.log('BUY CREATE ADX, %.2f' % self.data.close[0])
                    self.buy()
                    num=num+1
                    lit.append((p[p.index('adx')+1],'buy'))
            #else:
                if (self.adx[-3]>25 and self.adx[-2]<=25 and self.adx[-1]<25 and self.adx[0]<25):
                    self.log('SELL CREATE ADX, %.2f' % self.data.close[0])
                    self.sell()
                    num=num+1
                    lit.append((p[p.index('adx')+1],'sell'))
                 
        if 'ema' in self.list:
            #if not self.position:
                if (self.data.close[-1]>self.ema[-1] and self.data.close[0]<=self.ema[0]):
                    self.log('SELL CREATE EMA, %.2f' % self.data.close[0])
                    self.sell()
                    num=num+1
                    lit.append((p[p.index('ema_12')+1],'sell'))
                if (self.data.close[-1]<self.ema[-1] and self.data.close[0]>=self.ema[0]):
                    self.log('BUY CREATE EMA, %.2f' % self.data.close[0])
                    self.buy()
                    num=num+1
                    lit.append((p[p.index('ema_12')+1],'buy'))
                
        if 'bband' in self.list:
            #if not self.position:
                if (self.data.close[-1]<self.bbandup[-1] and self.data.close[0]>=self.bbandup[0]):
                    self.log('SELL CREATE BBAND, %.2f' % self.data.close[0])
                    self.sell()
                    num=num+1
                    lit.append((p[p.index('mavg')+1],'sell'))
                if (self.data.close[-1]>self.bbandlow[-1] and self.data.close[0]<=self.bbandlow[0]):
                    self.log('BUY CREATE BBAND, %.2f' % self.data.close[0])
                    self.buy()
                    num=num+1
                    lit.append((p[p.index('mavg')+1],'buy'))
                    
                    
                

        
        #correlation in case of 2 signal in the same day
        file = open("File.txt", "r") 
        seuil=float(file.read())
        if num>1:
            som=0
            R=0
            for x in lit:
                som=som+float(x[0])
                if x[1]=='buy':
                    R=R+float(x[0])*1
                elif x[1]=='sell':
                    R=R+float(x[0])*(-1)

            R=R/som
            if R>seuil:
                self.log('Final decision:BUY CREATE, %.2f' % self.data.close[0])
                self.buy()
            elif R<seuil:
                self.log('Final decision:SELL CREATE, %.2f' % self.data.close[0])
                self.sell()
            elif R==seuil:
                self.log('Final decision:HOLD, %.2f' % self.data.close[0])


                    
           
