import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import keras
from keras.models import load_model
from agent import AI_Trader
import sys
import time
import fxcmpy
import datetime as dt
import yaml
import socketio
import math
import json
import matplotlib.pyplot as plt
import numpy as np
import random
import sys



def SimulateTrade(currency_pair,lotSize,con):
    #connection obejct
    con = con

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
        data_stream = on_tick()
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


    #variables
    currency_pair=currency_pair
    lotSize = lotSize
    data_samples = 20
    window_size = 7


    trained_model = load_model("models/ai_trader_50.h5")
    trader = AI_Trader(window_size, False, "ai_trader_50.h5")

    state = CreateState(window_size + 1)
    total_profit = 0
    trade_ids = []
    
    #trading loop
    while (con.is_connected() == True):
        for t in range(data_samples):
            action = trader.act(state)
            print(action)
            next_state = CreateState(window_size + 1)
            reward = 0
            

            if action == 1:
                tradeOrder = placeMarketOrder(currency_pair, lotSize)
                dfIDs = con.get_open_positions()['tradeId']
                trade_ids = dfIDs.tolist()

            elif action == 2 and len(trade_ids) > 0:
                #print(trade_ids)
                position_id = trade_ids.pop(0)
                position = int(position_id) #change dtype to int
                closePosition(position, lotSize)
            
                #REWARD = GROSS P/L
                reward = float(con.get_closed_positions()['grossPL'][-1:])
                #print("PROFIT",reward)
                total_profit += reward
            
            if t == data_samples - 1 :
                #when approaching end of session close all open positions
                con.close_all()
                done = True

            else:
                done = False

            trader.memory.append((state, action, reward, next_state, done))
            state = next_state 
            time.sleep(300) #slows down model allowing it to view price changes before acting

            if done:
                #print("########################")
                #print("TOTAL PROFIT: {}".format(total_profit))
                #print("Final Inventory", trade_ids)
                #print("########################")

                profit = str(total_profit)

    return "Profit/Loss generated: " + profit 

