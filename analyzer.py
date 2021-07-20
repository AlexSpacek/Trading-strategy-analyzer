#class which stores historical daily candles for a given ticker 
#it has different methods that each generate different buy/sell signals (different swing trading strategies)
#then the final method analyzes the profitability of the buy/sell signals
import indicators
import numpy as np
import pandas as pd
class Analyzer:

  def __init__(self,*,ticker ,data):
    self.data = data
    self.ticker = ticker

  def methodBuy_Simple(self): #first trading strategy for generating buy/sell signals, todo: name the methods
    buySignal = np.zeros(self.data["Close"].size, dtype=int)
    #signal = macd.ewm(span=sig, adjust=False).mean()
    macd = indicators.macd(self.data, 12, 26, 9, "Close")
    zero_crossings = np.add(np.where(np.diff(np.sign(macd["signal"]))>0),1) #calculates indexes where macd signal crossed zero to positive, +1 to get the correct day
    buySignal[zero_crossings[0]] = 1 
    return buySignal
  
  def methodBuy_Mcstoch_ut1(self):
    # McStoch 1 buy signal in uptrend (macd signal > 0)
    # Previous day red and today green
    buySignal = np.zeros(self.data["Close"].size, dtype=int)
    # calculate mcstoch
    mcs = indicators.mcstoch(self.data, fl=12, sl=26, sig=9, price="Close", period=14, sk=2, sd=4)
    macd = indicators.macd(self.data, fl=12, sl=26, sig=9, price="Close")
    # evaluate the signal
    buySignal = (mcs["green"].gt(mcs["red"])) & (macd["signal"] > 0)
    return buySignal.astype("int").to_numpy()

  def methodBuy_Mcstoch_ut2(self):
    # McStoch 2 buy signal in uptrend
    # previous day red, today blue and close higher
    buySignal = np.zeros(self.data["Close"].size, dtype=int)
    # calculate mcstoch
    mcs = indicators.mcstoch(self.data, fl=12, sl=26, sig=9, price="Close", period=14, sk=2, sd=4)

    return buySignal
  
  def methodBuy_Mcstoch_ut3(self):
    # McStoch 3 buy signal in uptrend (macd signal > 0)
    # previous day blue, today green 
    buySignal = np.zeros(self.data["Close"].size, dtype=int)
    # calculate mcstoch
    mcs = indicators.mcstoch(self.data, fl=12, sl=26, sig=9, price="Close", period=14, sk=2, sd=4)
    macd = indicators.macd(self.data, fl=12, sl=26, sig=9, price="Close")
    # evaluate the signal
    buySignal = (mcs["green"].gt(mcs["blue"])) & (macd["signal"] > 0)
    return buySignal.astype("int").to_numpy()

  def methodBuy_Mcstoch_ut4(self):
    # McStoch 4 buy signal in uptrend
    # previous day blue a close < open, today blue and close > open 
    buySignal = np.zeros(self.data["Close"].size, dtype=int)
    # calculate mcstoch
    mcs = indicators.mcstoch(self.data, fl=12, sl=26, sig=9, price="Close", period=14, sk=2, sd=4)
    
    return buySignal
  
  def methodSell_Mcstoch(self):
    # McStoch sell signal
    # red day is a sell signal
    # calculate mcstoch
    mcs = indicators.mcstoch(self.data, fl=12, sl=26, sig=9, price="Close", period=14, sk=2, sd=4)
    return mcs["red"].to_numpy()

  def methodSell_Simple(self): #first trading strategy for generating buy/sell signals, todo: name the methods
    sellSignal = np.zeros(self.data["Close"].size, dtype=int)
    #signal = macd.ewm(span=sig, adjust=False).mean()
    macd = indicators.macd(self.data, 12, 26, 9, "Close")
    zero_crossings = np.add(np.where(np.diff(np.sign(macd["signal"]))<0),1) #calculates indexes where macd signal crossed zero to positive, +1 to get the correct day
    sellSignal[zero_crossings[0]] = 1
    return sellSignal

  def signalOr(self, signal1, signal2):
  # takes two signals and return their boolean OR
    return np.logical_or(signal1, signal2).astype("int")
  
  def signalSorter(self,buySignal,sellSignal):
    helper = 0
    zero_data = np.zeros(shape=(len(buySignal),2))
    d = pd.DataFrame(zero_data, columns=["buy","sell"])
    for j in range(0,len(buySignal)):
      if buySignal[j]==1&helper==0:
        d["buy"][j]=1
        helper = 1
      elif sellSignal[j]==1&helper==1: 
        d["sell"][j]=1
        helper = 0
    return d
    
  def profit(self,*,buyMethodName,sellMethodName,capitalForEachTrade,comission):   #method for calculating profit, inputs: how much money is spent on each trade and the name of the trading strategy
    if buyMethodName == 'Simple':
        buySignal = self.methodBuy_Simple()
    elif buyMethodName == 'Mcstoch_ut1':
        buySignal = self.methodBuy_Mcstoch_ut1()
    else:
        print('This method is not impplemented')    
    if sellMethodName == 'Simple':    
        sellSignal = self.methodSell_Simple()
    elif sellMethodName == 'Mcstoch':
        sellSignal = self.methodSell_Mcstoch()    
    else:
        print('This method is not implemented')    
    sorted_signals = self.signalSorter(buySignal,sellSignal)   
    Nbuys = np.sum(sorted_signals["buy"]).astype(int)
    zero_data = np.zeros(shape=(Nbuys,11)) 
    outputFrame = pd.DataFrame(zero_data, columns=["buy_date","buy_price","buy_value","position","sell_date","sell_price","sell_value","comission","good_trade?","profit[%]","profit[$]"])
    outputFrame["buy_date"] = self.data.loc[np.where(sorted_signals["buy"]==1)[0],"Date"].reset_index(drop=True)
    outputFrame["buy_price"] = self.data.loc[np.where(sorted_signals["buy"]==1)[0],"Close"].reset_index(drop=True)
    outputFrame["sell_date"] = self.data.loc[np.where(sorted_signals["sell"]==1)[0],"Date"].reset_index(drop=True)
    outputFrame["sell_price"] = self.data.loc[np.where(sorted_signals["sell"]==1)[0],"Close"].reset_index(drop=True)
    outputFrame["buy_value"] = capitalForEachTrade
    outputFrame["position"] = outputFrame["buy_value"]/outputFrame["buy_price"]
    outputFrame["sell_value"] = outputFrame["position"]*outputFrame["sell_price"]
    outputFrame["comission"] = comission
    outputFrame.loc[outputFrame["sell_value"]>outputFrame["buy_value"] ,"good_trade?"] = 1
    outputFrame["profit[$]"] = outputFrame["sell_value"]-outputFrame["buy_value"]
    outputFrame["profit[%]"] = outputFrame["profit[$]"]/outputFrame["buy_value"]
    return outputFrame

