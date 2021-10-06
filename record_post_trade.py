# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 23:57:53 2021

@author:Luca Incarbone

Record data around opening marcket to be used in the future to improove your 
algorithm or change the tresholds to improove the gain.


- set buy/sell at 15:26  (running OTAD.py script)
- after 16:00 sell at any gain and set stopLOSSES


run record_post_trade.py after 19:00 daily (before next trade)
	
run DDD.py to run the analysis on recorded database to test possible trade and simulate the possible past gain


"""

from credentials import get_cred 
from tvDatafeed import TvDatafeed,Interval
import pandas as pd
from datetime import datetime

def veryfy_trade(one_trade,low_to_buy,high_to_sell):
    
    bought = False
    sold = False
    #do not buy after 15:39
    one_trade_buy = one_trade.between_time('15:19', '15:39')
    for i in range(len(one_trade_buy)):
        if one_trade_buy.iloc[i]['low']<=low_to_buy:
            bought = True
            
    # order after 15:26
    one_trade_sell = one_trade.between_time('15:26', '17:01')
    for i in range(len(one_trade_sell)):
        if one_trade_sell.iloc[i]['high']>=high_to_sell:
            sold = True
    if bought and sold:
        return "OK"
    elif bought:
        return "Losses"
    else:
        return "noTrade"

def extract_data(file_n):
    
    #get data 5m resolution 
    df = pd.read_csv(file_n, index_col=0, parse_dates=True)
        
    return df


username,password=get_cred('tradingview');

# you need to run previously the credentials.py script to update a valid credential
tv=TvDatafeed(username=username, password=password)
data = tv.get_hist('WHSELFINVEST:USTECH100CFD','WHSELFINVEST',interval=Interval.in_1_minute,n_bars=1000)
print(data)

# data=pd.read_csv('DB/out.csv')
# print(data)


# str_date = "2021-07-02" 
# data_day = data.loc[str_date:str_date]
# start=data_day.between_time('15:19','15:24')

str_date = datetime.today().strftime('%Y-%m-%d')
data_day = data
one_trade = data_day.between_time('15:19', '17:01')


# BackUP data for future analysis
USTESCH100_data = tv.get_hist('WHSELFINVEST:USTECH100CFD','WHSELFINVEST',interval=Interval.in_1_minute,n_bars=5000)
USSP500_data = tv.get_hist('WHSELFINVEST:USSP500CFD','WHSELFINVEST',interval=Interval.in_1_minute,n_bars=5000)
WALLSTREET_data = tv.get_hist('WHSELFINVEST:WALLSTREETCFD','WHSELFINVEST',interval=Interval.in_1_minute,n_bars=5000)
# BakUp just opening market timewindow
USTESCH100_d = USTESCH100_data.between_time('15:00', '19:00')
USSP500_d = USSP500_data.between_time('15:00', '19:00')
WALLSTREET_d = WALLSTREET_data.between_time('15:00', '19:00')
#save to csv file
USTESCH100_d.to_csv(str('DB/USTECH100/1m/'+str_date+'_dailyRecord.csv'))
USSP500_d.to_csv(str('DB/USSP500/1m/'+str_date+'_dailyRecord.csv'))
WALLSTREET_d.to_csv(str('DB/WALLSTREET/1m/'+str_date+'_dailyRecord.csv'))

#Backup 5m resolution
USTESCH100_data = tv.get_hist('WHSELFINVEST:USTECH100CFD','WHSELFINVEST',interval=Interval.in_5_minute,n_bars=5000)
USSP500_data = tv.get_hist('WHSELFINVEST:USSP500CFD','WHSELFINVEST',interval=Interval.in_5_minute,n_bars=5000)
WALLSTREET_data = tv.get_hist('WHSELFINVEST:WALLSTREETCFD','WHSELFINVEST',interval=Interval.in_5_minute,n_bars=5000)

#consider past values to be add to the output file
USP500_df = extract_data( ".\\DB\\USSP500\\5m\\USSP500_5m_Record.csv")
USTECH100_df = extract_data( ".\\DB\\USTECH100\\5m\\USTECH100_5m_Record.csv")
WALLSTREET_df = extract_data( ".\\DB\\WALLSTREET\\5m\\WALLSTREET_5m_Record.csv")

# concatenate the old database and the new data to avoid data redundancy
USSP500_d=pd.concat([USP500_df,USSP500_data])
USSP500_d = USSP500_d[~USSP500_d.index.duplicated()]

USTESCH100_d=pd.concat([USTECH100_df,USTESCH100_data])
USTESCH100_d = USTESCH100_d[~USTESCH100_d.index.duplicated()]

WALLSTREET_d=pd.concat([WALLSTREET_df,WALLSTREET_data])
WALLSTREET_d = WALLSTREET_d[~WALLSTREET_d.index.duplicated()]

#save to csv file
USTESCH100_d.to_csv(str('DB/USTECH100/5m/USTECH100_5m_Record.csv'))
USSP500_d.to_csv(str('DB/USSP500/5m/USSP500_5m_Record.csv'))
WALLSTREET_d.to_csv(str('DB/WALLSTREET/5m/WALLSTREET_5m_Record.csv'))
