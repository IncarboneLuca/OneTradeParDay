# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 19:55:30 2021

Data Driven Decision

Analyise Data aleileble to improove the market strategy that is at the end 
define input for OTAD.py script

Input define : 1m trade in the intersted time interval

The goal of this script is to find out the best strategy to increase gain in 
long term. Define two main strategy to improove and compare
        - Define best choise of the price tresholds
        - Define multiple trade to optimise long term gain
        - analyse the correlation beetween factor as day in the week to adapt the strategy


Rules to respect the computed prediction:
    - at 15:40 if you hold a position with possible gain SELL or set a 
    MouvingLimit (but this script consider sold at 15:40 positive value)

@author: Luca Incarbone
"""

from credentials import get_cred 
from tvDatafeed import TvDatafeed,Interval
import mplfinance as mpf
import pandas as pd
import csv
import math
import os
import matplotlib.pyplot as plt
import numpy

from datetime import datetime
from dateutil.rrule import DAILY, rrule, MO, TU, WE, TH, FR

# time to start collecting data usefull to choose the prices
start_time='15:15'
# ready to set the position on the market
end_time='15:26'
# in case open position human decision driven buy or leave (if is positive gain --> SELL)
exit_time='16:45'
# to analyze if some hors after is interesting for exit trade strategy
stop_time='19:00'

# Verify if the defined trade is succesfull or not
def veryfy_trade(one_trade,low_to_buy,high_to_sell,sL,start_index,stop_time_buy=''):
    """With a given data will compute if the trade succeed """
    # defautl value for stop buying
    if stop_time_buy=='':
        stop_time_buy='15:45' 
    bought = False
    sold = False
    stopLoss = False
    margin=False
    bought_index=0
    sold_index=0
    sl_index=0
    #do not buy after 15:39
    # one_trade_buy = one_trade.between_time(start_time, '15:39')    
    one_trade_buy = one_trade.between_time('15:29', stop_time_buy) 
    # order after 15:26
    
    for i in range(start_index,len(one_trade)-1-start_index):
        # if it has been bought 
        if bought:
            #verify in case hasn't been sold if the lower lever is lower than stopLosses level
            if one_trade.iloc[i]['low']<=sL and not sold:
                stopLoss=True
                sl_index = i
                # end_trade = one_trade.loc[i]['time']
            # if the stop losses hasn't been activated and the ctrade hasn't ended (sold) 
            # verify if it has the level higher than sold level
            elif one_trade.iloc[i]['high']>=high_to_sell and not sold and not stopLoss:
                sold = True
                sold_index=i
                # end_trade = one_trade.loc[i]['time']
            elif one_trade.iloc[i]['high']>=low_to_buy and not sold:
                margin = True
        # verify if the buy level is satify (not after the time limitation)
        elif one_trade.iloc[i]['low']<=low_to_buy and i < len(one_trade_buy):
            bought = True
            bought_index=i
            #verify in case hasn't been sold if the lower lever is lower than stopLosses level
            if one_trade.iloc[i]['low']<=sL and not sold:
                stopLoss=True
                sl_index = i
            
    return bought_index, sold_index, sl_index, bought, sold, stopLoss, margin

# Record on a report the data about the trade
def recording_data(d_day, str_d,sold, stopLoss, bought,p_Sell,p_Buy,p_StopLoss,pos_gain, n_trade) : 
    
    # 
      
    #  RECORDING DATA
    if n_trade == '_1':
        d_day = d_day.between_time('15:15','16:30')
    else:
        d_day = d_day.between_time('15:15','15:40')
    if sold:
        g_l = (((((p_Sell/p_Buy)*100)-100)*150)/100)+1
        mpf.plot(d_day,hlines=dict(hlines=[p_StopLoss,p_Buy,p_Sell],colors=['k','g','r'],linestyle='-.'), type='candle',style='yahoo',volume=False,savefig=str('img/USTECH100/ANL/'+n_trade+'/'+str_d + n_trade+".png"))
        
        if n_trade == '_1':
            export_day_trend(str_d,'GainPrev')
        
    elif stopLoss:
        g_l= 1+((1-(p_Buy/p_StopLoss))*150)
        mpf.plot(d_day,hlines=dict(hlines=[p_StopLoss,p_Buy,p_Sell],colors=['r','g','k'],linestyle='-.'), type='candle',style='yahoo',volume=False,savefig=str('img/USTECH100/ANL/'+n_trade+'/'+str_d + n_trade+".png"))
        
        if n_trade == '_1':
            export_day_trend(str_d,'LossPrev')
        
    elif bought:
        if pos_gain:
            g_l = 1.1
        else:
            g_l = 0.9
        mpf.plot(d_day,hlines=dict(hlines=[p_StopLoss,p_Buy,p_Sell],colors=['k','r','k'],linestyle='-.'), type='candle',style='yahoo',volume=False,savefig=str('img/USTECH100/ANL/'+n_trade+'/'+str_d + n_trade+".png"))
        
        if n_trade == '_1':
            export_day_trend(str_d,'NeutralPrev')
        
    else:
        g_l = 1
        mpf.plot(d_day,hlines=dict(hlines=[p_StopLoss,p_Buy,p_Sell],colors=['k','k','k'],linestyle='-.'), type='candle',style='yahoo',volume=False,savefig=str('img/USTECH100/ANL/'+n_trade+'/'+str_d + n_trade+".png"))
        
        if n_trade == '_1':
            export_day_trend(str_d,'NeutralPrev')
        
    prediction = Predict_trade(str_d)
    
    with open(os.path.join(".\\report\\",'Report'+str_date_today+'.csv').replace("\\","/"), mode='a', newline='') as global_file_list:
        w_f = csv.writer(global_file_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # w_f.writerow(['Date','Buy', 'Sell','StopLoss','Gain or Loss'])
        w_f.writerow([str_d,round(p_Buy), round(p_Sell),round(p_StopLoss),round(g_l,2), prediction, n_trade])
        global_file_list.close()
    return g_l

# get the list of file to use 
def collect_list_file(folder_name):
    """Return file list of  specified folder """
    # COLLECT files to analyse (1m resolution)
    f_list=[]
    # get the whole list of file in src Folder
    for root, dirs, files in os.walk(folder_name):
    	for file in files:
            # append the file name to the list
    		f_list.append(os.path.join(folder_name, file).replace("\\", "/"))
    
    return f_list

# Compute the enter trade price
def get_buy_price(data_day):
    """Select the value before opening market time and compute the enter trade price"""
    start=data_day.between_time(start_time,end_time)
    start_value=0
    for i in range(len(start)):
        start_value+=start.iloc[i]['open']+start.iloc[i]['close']+start.iloc[i]['high']+start.iloc[i]['low']
    # start_value+=start.iloc[1]['open']+start.iloc[1]['close']+start.iloc[1]['high']+start.iloc[1]['low']
    start_value=start_value/len(start)/4
    return start_value

# Extract data from past recorded trades
def extract_data(file_n):
    """Select the last day availeble on the CSV file and return value """
    
    # dtypes = [datetime, str, float, float,float,float,float] 
    df = pd.read_csv(file_n, index_col=0, parse_dates=True)
    # df = df.between_time(df['datetime'][len(df)-1], df['datetime'][len(df)-1])
    return df

def extract_data_day(file_n):
    """Select the last day availeble on the CSV file and return value """
    
    # dtypes = [datetime, str, float, float,float,float,float] 
    df = pd.read_csv(file_n, index_col=0, parse_dates=True)
    # df = df.between_time(df['datetime'][len(df)-1], df['datetime'][len(df)-1])
    str_date = os.path.splitext(os.path.basename(file_n))[0]
    str_date=str_date[:10]
    df = df.loc[str_date:str_date]
    df = df.between_time(start_time,stop_time)
    return df

# plot the day trend for future analysis
def export_day_trend(str_d, folder_name):
    
    d_day_prev = d_week.loc[str_d:str_d]
    d_day_prev = d_day_prev.between_time('00:00',start_time)
    mpf.plot(d_day_prev, type='candle',style='yahoo',volume=False,savefig=str('img/USTECH100/ANL/'+folder_name+'/'+str_d+".png"))
    
    return
# try to increase the success of the trade by correlating the day trend
def Predict_trade(str_d):
    """A correlation between day trend and higher chance to succeed (causation or not?)"""
    score = 0
    d_day_prev = d_week.loc[str_d:str_d]
    open_price = d_day_prev.between_time('00:01','00:05')
    # open_price = d_day_prev.between_time('00:01','00:15')
    preUSopne_price = d_day_prev.between_time('15:10','15:15')
    # preUSopne_price = d_day_prev.between_time('15:00','15:19')
    o_p = open_price.iloc[:, 1:4].mean(axis=1)[0]
    oUS_p = preUSopne_price.iloc[:, 1:4].mean(axis=1)[0]
    
    if o_p > oUS_p:
        loss_day = (o_p-oUS_p)/(o_p/100)
        score+=loss_day
    else:
        gain_day = (oUS_p-o_p)/(o_p/100)
        score-=gain_day
    return score



# get file list
f_list_1m = collect_list_file(".\\DB\\USTECH100\\1m")
# f_list_5m = collect_list_file(".\\DB\\USTECH100\\5m")

#get data 5m resolution 
d_week = extract_data(".\\DB\\USTECH100\\5m\\USTECH100_5m_Record.csv")

# balance
balance_init = 300
balance = balance_init

# threshold definition
percent_buy=99.86
percent_sell=100.19
percent_sL=99.84
# get today date
str_date_today = datetime.today().strftime('%Y-%m-%d')
#open CSV file to store results
with open(os.path.join(".\\report\\",'Report'+str_date_today+'.csv').replace("\\","/"), mode='w+', newline='') as global_file_list:
        w_f = csv.writer(global_file_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w_f.writerow(['Date','Buy', 'Sell','StopLoss','Gain or Loss','Predict','Trade number'])
        global_file_list.close()
        
# treat the all listed files
for i in range(len(f_list_1m)):

    path=os.path.dirname(f_list_1m[i])
    
    d_day = extract_data_day(f_list_1m[i])
    start_index=0
    print((f_list_1m[i]))
    
    # test first trade if condition seems good 
    #FIRST 10 record are 3min candles so ignore them
    if i>10 :
        
        min4min_candle = d_day.between_time('15:19','15:28') 
        low_price_tmp = 100000000
        for k in range(len(min4min_candle)-1):
            if min4min_candle.iloc[k]['low'] < low_price_tmp:
                low_price_tmp = min4min_candle.iloc[k]['low']
        open_market_candle = d_day.between_time('15:29','15:30')  
        open_price = open_market_candle.iloc[0]['open']
        close_price = open_market_candle.iloc[0]['close']
        open_price_2 = open_market_candle.iloc[1]['open']
        close_price_2 = open_market_candle.iloc[1]['close']
        low_price_candle = open_market_candle.iloc[0]['low']
        # print(open_price)
        # print(close_price)
        # RED candle
        if open_price > close_price and  low_price_candle > low_price_tmp:#or open_price_2 > close_price_2:
            condition_to_buy_at_open_market =True
            p_Buy = d_day.between_time('15:30','15:30').iloc[0]['open']
            # 0.10 %
            p_Sell = p_Buy/100*100.1
            # -0.05 %
            p_StopLoss = p_Buy/100*99.95
            # bought at 15:31 so first candle 15:30 must be ignored in verification
            d_day_trade = d_day.between_time('15:30','16:30')
            # test trade
            bought_index, sold_index, sl_index, bought, sold, stopLoss, pos_gain = veryfy_trade(d_day_trade,p_Buy,p_Sell,p_StopLoss,start_index,stop_time_buy=exit_time)
            # print(bought_index)
            # print( sold_index)
            # print( sl_index)
            # Update strat index to let second trade append
            if sold :
                start_index = sold_index
                # print(sold_index)
            elif stopLoss:
                start_index = sl_index
                # print(sl_index)
            else :
                start_index=1
                if bought:
                    print("ERROR bought but never sold first trade")
            
            str_d = os.path.splitext(os.path.basename(f_list_1m[i]))[0][:10]
            
            g_l = recording_data(d_day,str_d,sold, stopLoss, bought,p_Sell,p_Buy,p_StopLoss,pos_gain,'_0')  
            
            balance= balance*g_l      

    # compute prices
    sv = get_buy_price(d_day)
    p_Buy = sv/100*percent_buy
    p_Sell = sv/100*percent_sell
    p_StopLoss = p_Buy/100*percent_sL
    
    # test trade
    bought_index, sold_index, sl_index, bought, sold, stopLoss, pos_gain = veryfy_trade(d_day,p_Buy,p_Sell,p_StopLoss,start_index,stop_time_buy=exit_time)
    
    # mpf.plot(data.between_time(start_time, end_time, include_start=True, include_end=True, axis=None), type='candle',style='yahoo',volume=True)
    # mpf.plot(data, type='candle',style='yahoo',volume=True)
    # one_trade = data_day.between_time(start_time, stop_time)
    str_d = os.path.splitext(os.path.basename(f_list_1m[i]))[0][:10]
    
    g_l = recording_data(d_day,str_d,sold, stopLoss, bought,p_Sell,p_Buy,p_StopLoss,pos_gain,'_1')  
    balance= balance*g_l      

print("final balance")
print(round(balance))
print("percentage gain")
print(round((balance/(balance_init/100))))
# #remake the computation for older recorded trade
# d_week = extract_data(".\\DB\\2021-07-13_15m_Record.csv")
# list_file_15m = pd.bdate_range('2021-04-28', '2021-07-02')
# trade_res=['L','L','N','L','L','G','L','L','L','L','G','G','G','G','L','L','N','L','G','G','G','G','N','N','L','N','L','N','L','L','L','G','L','L','L','N','N','G','L','G','N','N','L','N','G','L','N','N']
# # with open(os.path.join(".\\report\\",'Report'+str_date_today+'_old.csv').replace("\\","/"), mode='w+', newline='') as global_file_list:
# #     w_f = csv.writer(global_file_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# #     # w_f.writerow(['Date','Buy', 'Sell','StopLoss','Gain or Loss'])
# #     w_f.writerow(['Notrade','Gain','Loss', 'Trade'])
# #     global_file_list.close()
  
# loss=[]
# gain=[]
# no_trade=[]
# for k in range(len(list_file_15m)):
    
#     #  Convert to string the date
#     date_time_obj = list_file_15m[k].strftime( '%Y-%m-%d %H:%M:%S')

#     # w_f.writerow(['Date','Buy', 'Sell','StopLoss','Gain or Loss'])    
#     t_res = Predict_trade(date_time_obj[:10])
#     if trade_res[k] == 'N':
#         export_day_trend(date_time_obj[:10], 'TEST_OLD_TRADE/Notrade')
#         no_trade.append(t_res)
#     elif trade_res[k] == 'G':
#         export_day_trend(date_time_obj[:10], 'TEST_OLD_TRADE/Gain')
#         gain.append(t_res)
#     elif trade_res[k] == 'L':
#         export_day_trend(date_time_obj[:10], 'TEST_OLD_TRADE/Loss')
#         loss.append(t_res)
# print(min(loss))
# print(max(loss))
# print(min(gain))
# print(max(gain))
# print(min(no_trade))
# print(max(no_trade))
# bins = numpy.linspace(-2, 2, 10)

# plt.hist([loss, gain,no_trade], bins, label=['loss', 'gain','no trade'])
# plt.legend(loc='upper right')
# plt.show()
  