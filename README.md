# Trading strategy analyzer
Framework for developing and backtesting strategies for swing trading based on technical analysis indicators. Compromises of multiple self-functioning blocks. ```scraper.py``` holds class for storing, loading and scraping stock data from [yahoo finance](https://finance.yahoo.com/). ```indicators.py``` holds multiple functions for technical indicators and ```analyzer.py``` holds trading strategies and methods for evaluating trades.

### Requirements
* pandas
* numpy
* yfinance

# Scraper

Scraped data can be stored into corresponding csv file, if called on the same stock again, it loads the data from the csv file and updates them if required. Saving data can be disabled if desired. Default settings are save 1 year of data from today. Inputs *edate* and *date* needs to be same types as are default values, defining them can lead to unexpected behaviour as there is no check present.

Class | Inputs | Outputs 
------|------------|--------
```stock_daily()``` | *ticker*: string, as presented on the stock exchange <br> *edate*: end of data collection, def = ```dt.date.today()```<br> *delta*: length of data to grab, def = ```dt.timedelta(days=365)```<br> *pth*: string, where to save data, def = ```os.getcwd()``` <br> *save*: bool, save data? def = True| pandas DataFrame with following columns: <br> ```"Date"```: datetime64[ns] <br> ```"Open"```: float64 <br> ```"High"```: float64 <br> ```"Low"```: float64 <br> ```"Close"```: float64 <br> ```"Volume"```: int64

### Known issues
* Data are always from the day before, this is property of the yfinance package for data scraping
* On Sunday and Monday, stored data will try to update itself even if there are now new data present. Because of this, scraper runtime corresponds to scraping time (~0.4 sec), instead of loading time (~0.004 sec). I'll fix it.

# Indicators

File containing several functions for calculating basic technical analysis indicators. List of implemented indicators follows, definitions for more complex indicators are taken from investopedia or URL link is present in the description. Output is always defined as a DataFrame with first column ```["Date"]``` copied from the stock data and other columns corresponding to the indicator are written in the "Output columns" column.

Function | Parameters | Output columns | Description
----------|------------|---------|-------------
```sma()``` | *w*: length <br> *price*: which price column to use, default = ```"Close"``` | ```"SMA"``` | Simple moving average
```ema()``` | same as ```sma()``` | ```"EMA"``` | Exponential moving average
```macd()``` | *fl*: fast line length, def = 12 <br> *sl*: slow line length, def = 26 <br> *sig*: signal length, def = 9 <br> *price*: same as ```sma()``` | ```"macd", "signal", "histogram"``` | MACD (Moving average convergence divergence) <br> as defined by [Investopedia](https://www.investopedia.com/terms/m/macd.asp)
```stoch()``` | *period*: length of data period, def = 14 <br> *sk*: k line smoothing, def = 2 <br> *sd*: d line smoothing, def = 4 | ```"k", "d"``` | Stochastic Oscillator. Code copied from [here](https://www.learnpythonwithrune.org/pandas-calculate-the-stochastic-oscillator-indicator-for-stocks/)
```mcstoch()``` | Same inputs as ```macd()``` and ```stoch()``` | ```"green", "yellow", "red", "blue"``` | Combination of macd and stoch indicators to filter opportunities
```bollbands()``` | *period*: length of data period, def = 20 <br> *stdn*: # of std multipliers, def = 2 | ```"lower", "upper"``` | Bollinger bands as defined by [investopedia](https://www.investopedia.com/terms/b/bollingerbands.asp) 
```rsi()``` | *w*: period length, def = 14 <br> *price*: which column to use, def=```"Close"``` <br> *ema*: use sma or ema, bool, def = True | ```"RSI"``` | Relative strength index, code copied and modified from [here](https://www.roelpeters.be/many-ways-to-calculate-the-rsi-in-python-pandas/)
```vfi()``` | *period*: lookback period, def = 40 <br> *coef*: to be explained, def = 0.2 <br> *vcoef*: unusual volume levels limiter, def = 2.5 <br> *ssmooth*: = smoothing for ema, def = 5 | ```"vfi", "vfi_smooth, "histogram"``` | Volume flow indicator by Markos Katsanos. Code based on [tradingview indicator](https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/). <br> More information about the indicator can be found [here](https://precisiontradingsystems.com/volume-flow.htm) and [here](https://www.thatsucks.com/volume-flow-indicator-following-the-crowd-isnt-so-bad/)

Other indicators will be added in the future

# Buy & Sell signals
This section describes viable buy and sell signals developed and tested by this system

# Analyzer
