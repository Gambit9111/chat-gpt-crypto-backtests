import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG
import ta
from ta.utils import dropna

    # buy_threshold = 
    # sell_threshold = 
    # stop_loss_threshold = 
# ! 50 / 30 / 7 outperforms the market on btcusd daily since 2016



# Helper functions for each indicator
def SMA_indicator(series, window):
    series = pd.Series(series)
    return ta.trend.SMAIndicator(series, window=window).sma_indicator()

def Bollinger_High(series, window, window_dev):
    series = pd.Series(series)
    return ta.volatility.BollingerBands(series, window=window, window_dev=window_dev).bollinger_hband()

def Bollinger_Low(series, window, window_dev):
    series = pd.Series(series)
    return ta.volatility.BollingerBands(series, window=window, window_dev=window_dev).bollinger_lband()

def MFI(high, low, close, volume):
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    volume = pd.Series(volume)
    return ta.volume.MFIIndicator(high=high, low=low, close=close, volume=volume).money_flow_index()

def RSI(series, window):
    series = pd.Series(series)
    return ta.momentum.RSIIndicator(close=series, window=window).rsi()

def Stochastic(high, low, close, window):
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    return ta.momentum.StochasticOscillator(high=high, low=low, close=close, window=window).stoch()

def MACD(series, window_slow, window_fast, window_sign):
    series = pd.Series(series)
    macd = ta.trend.MACD(close=series, window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
    return macd.macd()

def StochRSI(series, window, smooth1, smooth2):
    series = pd.Series(series)
    stoch_rsi = ta.momentum.StochRSIIndicator(close=series, window=window, smooth1=smooth1, smooth2=smooth2)
    return stoch_rsi.stochrsi()

# Custom Strategy using Weighted Indicators
class WeightedIndicatorStrategy(Strategy):
    weights = {
        'MA_10_20': 4.30,
        'MA_18_20': 18.570,
        'MA_7_17': 5.750,
        'BollingerBands': 17.650,
        'MFI': 16.930,
        'RSI_21': 2.230,
        'Stochastics_53': 18.370,
        'MACD': 7.510,
        'StochRSI': 33.43
    }
    
    buy_threshold = 40
    sell_threshold = 30
    stop_loss_threshold = 10

    def init(self):
        # Calculating indicators using helper functions
        self.ma10 = self.I(SMA_indicator, self.data.Close, 10)
        self.ma20 = self.I(SMA_indicator, self.data.Close, 20)
        self.ma18 = self.I(SMA_indicator, self.data.Close, 18)
        self.ma7 = self.I(SMA_indicator, self.data.Close, 7)
        self.ma17 = self.I(SMA_indicator, self.data.Close, 17)

        self.bollinger_high = self.I(Bollinger_High, self.data.Close, 20, 2)
        self.bollinger_low = self.I(Bollinger_Low, self.data.Close, 20, 2)

        self.mfi = self.I(MFI, self.data.High, self.data.Low, self.data.Close, self.data.Volume)
        self.rsi = self.I(RSI, self.data.Close, 21)
        self.stochastics = self.I(Stochastic, self.data.High, self.data.Low, self.data.Close, 53)
        self.macd = self.I(MACD, self.data.Close, 26, 12, 9)
        self.stochrsi = self.I(StochRSI, self.data.Close, 14, 3, 3)
        
        self.entry_price = None  # Initialize entry price

    def next(self):
        # Calculating weighted sum of indicators
        weighted_sum = (
            (self.ma10 > self.ma20) * self.weights['MA_10_20'] +
            (self.ma18 > self.ma20) * self.weights['MA_18_20'] +
            (self.ma7 > self.ma17) * self.weights['MA_7_17'] +
            (crossover(self.data.Close, self.bollinger_high) or crossover(self.data.Close, self.bollinger_low)) * self.weights['BollingerBands'] +
            (self.mfi > 50) * self.weights['MFI'] +
            (self.rsi > 50) * self.weights['RSI_21'] +
            (self.stochastics > 50) * self.weights['Stochastics_53'] +
            (self.macd > 0) * self.weights['MACD'] +
            (self.stochrsi > 0.8) * self.weights['StochRSI']
        )
        
        # Check if we already have an open position
        if self.position:
            # Calculate the loss percentage if entry price is recorded
            if self.entry_price is not None:
                current_price = self.data.Close[-1]
                loss_percentage = (current_price - self.entry_price) / self.entry_price * 100

                # Sell if the stop-loss threshold is reached
                if loss_percentage <= -self.stop_loss_threshold:
                    self.position.close()
                    self.entry_price = None  # Reset entry price
                    return

        # Trading logic with adjusted thresholds
        if weighted_sum > self.buy_threshold:  # Adjusted buy threshold
            if not self.position:
                self.buy()
                self.entry_price = self.data.Close[-1]  # Record entry price
        elif weighted_sum < self.sell_threshold:  # Adjusted sell threshold
            if self.position:
                self.position.close()
                self.entry_price = None  # Reset entry price

# Load your data here
data = pd.read_csv("BTC-USD-1h-2018.csv", sep=',')
data = data.drop(columns=['Unnamed: 6'])
data = dropna(data)
data['Time'] = pd.to_datetime(data['Time'])
data = data.set_index('Time')

# Backtesting
bt = Backtest(data, WeightedIndicatorStrategy, cash=100000, commission=.002)

params = {
    'buy_threshold': range(30, 60, 5),
    'sell_threshold': range(20, 50, 5),
    'stop_loss_threshold': range(5, 15, 2)
}

# Run optimization
opt_stats = bt.optimize(**params, maximize='Equity Final [$]', constraint=lambda param: param.buy_threshold > param.sell_threshold)
print(opt_stats)
print(opt_stats._strategy)
# bt.plot()