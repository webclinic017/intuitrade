import os
import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as dates
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from pprint import pprint
from sklearn.preprocessing import StandardScaler, Normalizer
# import ta
#import ta
from sklearn.linear_model import LinearRegression
import numpy as np
import pylab
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import talib
from scipy import stats
from pandas_datareader import data as pdr
import warnings
import backtrader as bt
from Stratcorfinal import Strat
import dateutil.relativedelta
from datetime import timedelta
import yfinance as yf

yf.pdr_override()
warnings.simplefilter(action="ignore", category=RuntimeWarning)
# getting correlation and company tic
    #app(value,r,seuil)

#value = input('Company tic: ')
#r = input('Correlation degree: ')
#seuil = input('Threshold: ')
def app(value,r, seuil):
    with open("File.txt", "w") as f:
        f.write(seuil)
        f.close()
    r = float(r)

    year = str(datetime.datetime.today().year)
    lyear = lmonth = str((datetime.datetime.today() - timedelta(days=360)).year)
    month = str(datetime.datetime.today().month)
    lmonth = str((datetime.datetime.today() - timedelta(days=360)).month)
    day = str(int(datetime.datetime.today().day + 1))
    enddate = year + '-' + month + '-' + day
    strtdate = lyear + '-' + lmonth + '-' + day
    print(strtdate)
    print(enddate)
    data = pdr.get_data_yahoo(value, start=strtdate, end=enddate)
    #data=yf.download(value, start=strtdate, end=enddate)
    # data.to_csv(r'file.csv')
    # Below are the indicators extracted from library ta, you need to install ta library for it to work
    ind_macd, macdsignal, macdhist = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    ind_rsi = talib.RSI(data['Close'], timeperiod=14)
    ind_rsi1 = talib.RSI(data['Close'], timeperiod=5)
    ind_wr = talib.WILLR(data['High'], data['Low'], data['Close'], timeperiod=30)
    ind_ema = talib.EMA(data['Close'], timeperiod=14)
    ind_mfi = talib.MFI(data['High'], data['Low'], data['Close'], data['Volume'], timeperiod=14)
    # ind_cmf=ta.volume.chaikin_money_flow(data['High'],data['Low'],data['Close'], data['Volume'], n=20, fillna=True)
    ind_bbandup, middle, ind_bbandlow = talib.BBANDS(data['Close'], timeperiod=20)
    ind_adx = talib.ADX(data['High'], data['Low'], data['Close'], timeperiod=14)
    # ind_ichimoku=ta.trend.ichimoku_a(data['High'],data['Low'], n1=9,n2=26,visual=False, fillna=True)
    ind_stoch, pa = talib.STOCH(data['High'], data['Low'], data['Close'])
    ind_trix = talib.TRIX(data['Close'], timeperiod=5)
    ind_ad = talib.AD(data['High'], data['Low'], data['Close'], data['Volume'])
    sma50 = talib.SMA(data['Close'], timeperiod=5)
    sma200 = talib.SMA(data['Close'], timeperiod=20)

    ind_macd = ind_macd.rename("MACD_12_26")
    macdsignal = macdsignal.rename("Macd_signal")
    ind_rsi = ind_rsi.rename("rsi")
    ind_rsi1 = ind_rsi1.rename("rsi5")
    ind_wr = ind_wr.rename("wr")
    ind_ema = ind_ema.rename("ema_12")
    ind_mfi = ind_ema.rename("mfi_14")
    ind_bbandup = ind_bbandup.rename("mavg")
    ind_bbandlow = ind_bbandlow.rename("mavglow")
    ind_adx = ind_adx.rename("adx")
    ind_stoch = ind_stoch.rename("stoch_k")
    ind_trix = ind_trix.rename("trix_15")
    ind_ad = ind_ad.rename("adi")
    sma50 = sma50.rename("Close SMA50")
    sma200 = sma200.rename("Close SMA200")

    # joining the indicators in dataframe
    result = data.join(ind_macd).join(macdsignal).join(ind_trix).join(ind_ad).join(ind_rsi).join(ind_rsi1).join(
        ind_wr).join(ind_ema).join(ind_stoch).join(ind_mfi).join(ind_bbandup).join(ind_bbandlow).join(ind_adx).join(sma50,
                                                                                                                    rsuffix=' SMA50').join(
        sma200, rsuffix=' SMA200')

    path = value + '_all_indicators.csv'
    result.to_csv(path)
    name = str(value) + '_all_indicators.csv'
    # preparing the data
    df1 = pd.read_csv(name, index_col=0, low_memory=False)
    df = df1.iloc[:, 3:23]
    # df.drop("Macd_signal", axis=1,inplace=True)
    df.drop("rsi5", axis=1, inplace=True)
    df.drop("Volume", axis=1, inplace=True)
    df.drop("Adj Close", axis=1, inplace=True)
    # df.drop()
    # df.drop("Volume_x", axis=1,inplace=True)
    # fig=plt.figure()
    # fig.savefig(tmpfile, format='png')
    datee = list(df.index)
    pricee = df['Close'].values.tolist()
    df.reset_index(inplace=True)
    fd = df
    dat = []
    pric = []
    signal = []
    color = []
    size = []
    now = datetime.datetime.now()
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000.0)
    m = 10000.0
    # initialize indicators every month
    for i in range(30, 390, 30):
        # correlation
        df1 = pd.read_csv(name, index_col=0, low_memory=False)
        df = df1.iloc[:, 3:23]
        # df.drop("Macd_signal", axis=1,inplace=True)
        df.drop("rsi5", axis=1, inplace=True)
        df.drop("Volume", axis=1, inplace=True)
        df.drop("Adj Close", axis=1, inplace=True)
        datee = list(df.index)
        df.reset_index(inplace=True)
        df = df[i - 30:i]
        lis = []
        macd = df['MACD_12_26'].values.tolist()
        date = df['Date'].values.tolist()
        price = df['Close'].values.tolist()
        Rsi = df['rsi'].values.tolist()
        Mfi = df['mfi_14'].values.tolist()
        # cmf=df['cmf'].values.tolist()
        sm1 = df['Close SMA50'].values.tolist()
        sm2 = df['Close SMA200'].values.tolist()
        wr = df['wr'].values.tolist()
        stoch_k = df['stoch_k'].values.tolist()
        trix_15 = df['trix_15'].values.tolist()
        adx = df['adx'].values.tolist()
        ema_12 = df['ema_12'].values.tolist()
        mavgup = df['mavg'].values.tolist()
        macdsignal = df['Macd_signal'].values.tolist()
        try:
            mavglow = df['mavglow'].values.tolist()
        except:
            continue
        try:
            df.drop("mavglow", axis=1, inplace=True)
        except:
            continue
        corr = df.corr(method='spearman')
        #    print(corr)
        x = corr.loc[['Close'], :]
        x = x.iloc[:, 1:]
        #    print(x)
        for col in x.columns:
            if (x[col].values[0] >= r or x[col].values[0] <= (-r)):
                lis.append((col, x[col].values[0]))
        # generate indicators signal
        for x in lis:
            if 'macd' in x[0].lower():
                for i in range(len(macd)):
                    if ((macd[i - 3] < 0 and macd[i - 2] >= 0 and macd[i - 1] > 0 and macd[i] > 0)
                            or (macd[i - 1] < macdsignal[i - 1] and macd[i] >= macdsignal[i])):
                        signal.append("Buy_Macd")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("green")
                        size.append(10)
                        print('BUY_MACD_TEST')
                        print(macd[i - 3], macd[i - 2], macd[i - 1], macd[i])
                    elif ((macd[i - 3] > 0 and macd[i - 2] <= 0 and macd[i - 1] < 0 and macd[i] < 0)
                          or (macd[i - 1] > macdsignal[i - 1] and macd[i] <= macdsignal[i])):
                        signal.append("Sell_Macd")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("red")
                        size.append(10)
                        print('SELL_MACD_TEST')
                        print(macd[i - 3], macd[i - 2], macd[i - 1], macd[i])
                # RSI_Signal
            elif 'rsi' in x[0].lower():
                for i in range(len(Rsi)):
                    if (Rsi[i - 1] < 70 and Rsi[i] >= 70):
                        signal.append("Sell_Rsi")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("red")
                        size.append(15)
                        print('SELL_RSI_TEST')
                        print(date[i])
                        print(Rsi[i - 1], Rsi[i])
                    elif (Rsi[i - 1] > 30 and Rsi[i] <= 30):
                        signal.append("Buy_Rsi")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("green")
                        size.append(10)
                        print('BUY_RSI_TEST')
                        print(date[i])
                        print(Rsi[i - 1], Rsi[i])
                # MFI_Signal
            elif 'mfi' in x[0].lower():
                for i in range(len(Mfi)):
                    if (Mfi[i - 1] < 80 and Mfi[i] >= 80):
                        signal.append("Sell_Mfi")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("red")
                        size.append(10)
                    elif (Mfi[i - 1] > 20 and Mfi[i] <= 20):
                        signal.append("Buy_Mfi")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("green")
                        size.append(10)

                # Moving_Average_Signal
            # elif 'sma' in x[0].lower():
            #     for i in range(len(sm1)):
            #         if (sm1[i - 2] < sm2[i - 2] and sm1[i] > sm2[i]):
            #             signal.append("Buy_SMA")
            #             dat.append(date[i])
            #             pric.append(price[i])
            #             color.append("green")
            #             size.append(10)
            #         elif (sm1[i - 2] > sm2[i - 2] and sm1[i] < sm2[i]):
            #             signal.append("Sell_SMA")
            #             dat.append(date[i])
            #             pric.append(price[i])
            #             color.append("red")
            #             size.append(10)
                # William_wr Signal
            elif 'wr' in x[0].lower():
                for i in range(len(wr)):
                    if (wr[i - 1] < -20 and wr[i] >= -20):
                        signal.append("Sell_wr")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("red")
                        size.append(10)
                    elif (wr[i - 1] > -80 and wr[i] <= -80):
                        signal.append("Buy_wr")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("green")
                        size.append(10)
                # Stochastic Signal
            elif 'stoch' in x[0].lower():
                for i in range(len(stoch_k)):
                    if (stoch_k[i - 1] < 80 and stoch_k[i] >= 80):
                        signal.append("Sell_stoch_k")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("red")
                        size.append(10)
                        print('SELL_STOCH_TEST')
                        print(date[i])
                        print(stoch_k[i - 1], stoch_k[i])
                    elif (stoch_k[i - 1] > 20 and stoch_k[i] <= 20):
                        signal.append("Buy_stoch_k")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("green")
                        size.append(10)
                        print('BUY_STOCH_TEST')
                        print(date[i])
                        print(stoch_k[i - 1], stoch_k[i])
                # trix_15 Signal
            elif 'trix' in x[0].lower():
                for i in range(len(trix_15)):
                    if (trix_15[i - 1] < 0 and trix_15[i] >= 0):
                        signal.append("Buy_trix_15")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("green")
                        size.append(10)
                    elif (trix_15[i - 1] > 0 and trix_15[i] <= 0):
                        signal.append("Sell_trix_15")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("red")
                        size.append(10)
                # ADX Signal
            elif 'adx' in x[0].lower():
                for i in range(len(adx)):
                    if (adx[i - 3] < 25 and adx[i - 2] >= 25 and adx[i - 1] > 25 and adx[i] > 25):
                        signal.append("Buy_adx")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("green")
                        size.append(10)
                        print('BUY_ADX_TEST')
                        print(adx[i - 3], adx[i - 2], adx[i - 1])
                    elif (adx[i - 3] > 25 and adx[i - 2] <= 25 and adx[i - 1] < 25 and adx[i] < 25):
                        signal.append("Sell_adx")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("red")
                        size.append(10)
                        print('SELL_ADX_TEST')
                        print(adx[i - 3], adx[i - 2], adx[i - 1])
                # EMA Signal

            #        elif 'ema' in x[0].lower():
            #            for i in range(len(ema_12)):
            #                if (price[i-1]>ema_12[i-1] and price[i]<=ema_12[i]):
            #                     signal.append("Sell_Ema")
            #                     dat.append(date[i])
            #                     pric.append(price[i])
            #                     color.append("red")
            #                     size.append(10)
            #                if (price[i-1]<ema_12[i-1] and price[i]>=ema_12[i]):
            #                    signal.append("Buy_Ema")
            #                    dat.append(date[i])
            #                    pric.append(price[i])
            #                    color.append("green")
            #                    size.append(10)

            elif 'mavg' in x[0].lower():
                for i in range(len(mavgup)):
                    if (price[i - 1] < mavgup[i - 1] and price[i] >= mavgup[i]):
                        signal.append("Sell_BBAND")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("red")
                        size.append(10)
                    if (price[i - 1] > mavglow[i - 1] and price[i] <= mavglow[i]):
                        signal.append("Buy_BBAND")
                        dat.append(date[i])
                        pric.append(price[i])
                        color.append("green")
                        size.append(10)
        # calling backtrader and preparing the datafeed
        print(signal)
        s = ''
        for x in lis:
            s = s + x[0] + ',' + str(x[1]) + ','
        s = s[:-1]
        print(s)
        with open("MyFile.txt", "w") as f:
            f.write(s)
            f.close()
        try:
            ldare = df['Date'].iloc[0]
            dare = df['Date'].iloc[-1]
            year = str(dare[0:4])
            day = str(dare[8:10])
            month = str(dare[5:7])

            # now=now + dateutil.relativedelta.relativedelta(months=-2)
            # lyear=str(dare[8:10])
            dab = datetime.datetime(year=int(year), month=int(month), day=1)
            dab = dab.replace(day=1) - timedelta(days=1)
            dab = dab.replace(day=1) - timedelta(days=1)
            lmonth = str(dab.month)
            lyear = str(dab.year)
            llyear = str(int(lyear) - 1)
            enddate = year + '-' + month + '-' + day
            strtdate = llyear + '-' + month + '-' + day
            trtdate = lyear + '-' + lmonth + '-' + day
            print((strtdate, enddate, trtdate))
            data = pdr.get_data_yahoo(value, start=strtdate, end=enddate)
            data.to_csv(r'file.csv')
            data = bt.feeds.GenericCSVData(dataname='file.csv',
                                           fromdate=datetime.datetime(int(lyear), int(lmonth), int(day)),
                                           todate=datetime.datetime(int(year), int(month), int(day)),
                                           dtformat=('%Y-%m-%d'))
            # now=now + dateutil.relativedelta.relativedelta(months=+1)
            cerebro.adddata(data)
            cerebro.addstrategy(Strat)
            # set the cash with the final portfolio value from the last month
            cerebro.broker.setcash(m)
            print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
            cerebro.run()
            print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
            # having the final portfloio value
            m = cerebro.broker.getvalue()
            cerebro = bt.Cerebro()
            df = fd
        except:
            print('Exception')

    fig = go.Figure(data=go.Scatter(x=datee, y=pricee, name='Price'))
    fig.add_trace(go.Scatter(x=dat, y=pric, mode='markers', marker=dict(size=size,
                                                                        color=color), text=signal))
    fig.update_layout(title_text="Correlated indicators")
    #fig.write_html('Financial_Indicators.html', auto_open=True)
    st.plotly_chart(fig)


#app('AMZN','0.8','0.5')
value=st.sidebar.text_input('Company tic')
r=st.sidebar.number_input('Enter correlation degree')
seuil=st.sidebar.number_input('Enter threshold')
if st.sidebar.button('Enter'):
    app(value,r,str(seuil))
# plotting the data
# print (dat)
# print(color)
# print(signal)
#fig = go.Figure(data=go.Scatter(x=datee, y=pricee, name='Price'))
#fig.add_trace(go.Scatter(x=dat, y=pric, mode='markers', marker=dict(size=size,color=color), text=signal))
#fig.update_layout(title_text="Correlated indicators")
#fig.write_html('Financial_Indicators.html', auto_open=True)




