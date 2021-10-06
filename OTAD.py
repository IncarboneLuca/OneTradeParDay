# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 23:57:53 2021

@author: Luca Incarbone

Simple script to be run before opening market (3 minutes before)
to get the updated values and compute the entering price to set for the trade

"""

from credentials import get_cred 
from tvDatafeed import TvDatafeed,Interval
import mplfinance as mpf
import pandas as pd
import csv

def veryfy_trade(one_trade,low_to_buy,high_to_sell):
    
    bought = False
    sold = False

    for i in range(len(one_trade)):
        if one_trade.iloc[i]['low']<=low_to_buy:
            bought = True
        if one_trade.iloc[i]['high']>=high_to_sell:
            sold = True
    if bought and sold:
        return "OK"
    elif bought:
        return "Losses"
    else:
        return "noTrade"
    
def Predict_trade(dat):
    # print(str_d)
    score = 0
    open_price = dat.between_time('00:01','00:05')
    preUSopne_price = dat.between_time('15:15','15:19')
    o_p = open_price.iloc[:, 1:4].mean(axis=1)[0]
    oUS_p = preUSopne_price.iloc[:, 1:4].mean(axis=1)[0]
    
    if o_p > oUS_p:
        loss_day = (o_p-oUS_p)/(o_p/100)
        score+=loss_day
    else:
        gain_day = (oUS_p-o_p)/(o_p/100)
        score-=gain_day
    return score

username,password=get_cred('tradingview');
# you need to run previously the credentials.py script to update a valid credential
tv=TvDatafeed(username=username, password=password)
data = tv.get_hist('WHSELFINVEST:USTECH100CFD','WHSELFINVEST',interval=Interval.in_3_minute,n_bars=400)
# print(data)

# data=pd.read_csv('DB/out.csv')
# print(data)


# str_date = "2021-06-21" 
# data_day = data.loc[str_date:str_date]
# start=data_day.between_time('15:19','15:24')


# a causation hasn't been demonstrate, this is an advice data driven
prediction = Predict_trade(data)
if prediction>0:
    print('Good day to trade')
else:
    print('###########################')
    print('\tDO NOT TRADE TODAY!!!!')
    print('###########################')
data_day = data
start=data_day.between_time('15:19','15:24')
# start=data_day

# one_trade = data.between_time('15:19', '15:51')
# one_trade.to_csv('DB/out20k.csv')

start_value=start.iloc[0]['open']+start.iloc[0]['close']+start.iloc[0]['high']+start.iloc[0]['low']
# start_value+=start.iloc[1]['open']+start.iloc[1]['close']+start.iloc[1]['high']+start.iloc[1]['low']
start_value=start_value/4

sv = start_value
lowRiskBuy = sv/100*99.87
lowRiskSell = sv/100*100.19
medRiskBuy = sv/100*99.87
medRiskSell = sv/100*100.18
highRiskBuy = sv/100*99.75
highRiskSell = sv/100*100.2
riskBuy = sv/100*99.66
riskSell = sv/100*100.21

stopLosses = lowRiskBuy/100*99.86
cr = 0.999320144

print('\nStart value:')
print('\n\t'+str(round(start_value*cr,2)))
print('\nBuy:')
print('\n\t'+str(round(lowRiskBuy*cr,2)))
print('\nSell:')
print('\n\t'+str(round(lowRiskSell*cr,2)))
print('\t'+str(round(medRiskSell*cr,2)))
print('\nStopLosses')
print('\n\t'+str(round(stopLosses*cr,2)))
