import fxcmpy
import datetime as dt
import yaml
import socketio
import math
import json
import matplotlib.pyplot as plt
import numpy as np
import random
from collections import deque
from tqdm import tqdm
import sys
import yaml

#-------------------------------------------------------------stream data
def on_tick():
    df = con.get_candles(currency_pair, period='m1', columns = ['askclose'], number = window_size)
    return df 
#--------------------------------------------------------------historical data
def getData(currency_pair):
    start = dt.datetime(2020, 7, 15)
    stop = dt.datetime(2020, 8, 1)
    con.get_candles(currency_pair, period = 'D1', start=start, stop=stop )
    
#------------------------------------------------------------create state    
def CreateState(window_size):
    data_stream = on_tick(con, currency_pair)
    state = []
    state.append(data_stream)
    return np.array(state)  

#---------------------------------------------------------------plot performance
def plotData(dataSet):
    title = "Model's performance"
    plt.figure(figsize=(12.2,4.5))
    plt.scatter(dataSet.index, dataSet['Buy'], color = 'green', label='Buy Signal', marker = '^', alpha = 1)
    plt.scatter(dataSet.index, dataSet['Sell'], color = 'red', label='Sell Signal', marker = 'v', alpha = 1)
    plt.plot( dataSet['Data'],  label='Tick Data',alpha = 0.35)
       
    plt.title(title)
    plt.xlabel('Dates',fontsize=12)
    plt.ylabel('Price Value',fontsize=12)
    plt.legend(dataSet.columns.values, loc='upper left')

    return plt.show()
#-----------------------------------------------------------------place market order
def placeMarketOrder(currency_pair, lotSize):
    order = con.create_market_buy_order(currency_pair, lotSize)
    
    print("Market Order Placed")
    
#-----------------------------------------------------------------get list of open trades
def getOpenTrades():
    trade_ids = con.get_open_positions()['tradeId']
    
    #returns a trade_id df
    return trade_ids
    
#-----------------------------------------------------------------close specific position
def closePosition(trade_id, lotSize):
    con.close_trade(trade_id=trade_id, amount=lotSize)
    
    print("Position closed")
    
#------------------------------------------------------------------close all open positions
def killSwitch(currency_pair):
    con.close_all_for_symbol(currency_pair)
    con.close()
    print("All positions closed")
