from backtesting import Backtest, Strategy
from backtesting.lib import crossover, SignalStrategy, TrailingStrategy
from backtesting.test import GOOG  # Sample data
import numpy as np
import pandas as pd
import pywt
from ta.utils import dropna

class WaveletBollingerBandsStrategy(Strategy):
    n = 20  # Period for Bollinger Bands
    k = 2   # Number of standard deviations for Bollinger Bands
    atr_period = 14  # Period for ATR
    rsi_period = 14  # Period for RSI
    rsi_overbought = 70
    rsi_oversold = 30
    max_drawdown_percent = 15  # Maximum drawdown percentage

    def init(self):
        # Apply wavelet transform for noise reduction
        price = self.data.Close
        coeffs = pywt.wavedec(price, 'sym3', level=3)
        reconstructed_price = pywt.waverec(coeffs, 'sym3')
        self.drawdown = 0

        # Use reconstructed price for Bollinger Bands
        self.ma = pd.Series(reconstructed_price).rolling(self.n).mean()
        std = pd.Series(reconstructed_price).rolling(self.n).std()
        self.upper = self.ma + self.k * std
        self.lower = self.ma - self.k * std

        # MACD Indicator
        self.macd = MACD(price)

        # ATR for dynamic stop-loss and take-profit
        self.atr = ATR(self.data.High, self.data.Low, self.data.Close, self.atr_period)

        # RSI for additional confirmation
        self.rsi = RSI(price, self.rsi_period)

    def next(self):
        # Control drawdown
        if self.drawdown > self.max_drawdown_percent:
            return

        # Only trade if no open positions
        if not self.position:
            # Dynamic stop-loss and take-profit levels
            stop_loss = self.data.Close.iloc[-1] - 2 * self.atr.iloc[-1]
            take_profit = self.data.Close.iloc[-1] + 4 * self.atr.iloc[-1]

            # Long entry condition
            if (self.data.Close.iloc[-1] > self.upper.iloc[-1]) and (self.macd.iloc[-1] > 0) and (self.rsi.iloc[-1] < self.rsi_overbought):
                self.buy(sl=stop_loss, tp=take_profit)

            # Short entry condition
            elif (self.data.Close.iloc[-1] < self.lower.iloc[-1]) and (self.macd.iloc[-1] < 0) and (self.rsi.iloc[-1] > self.rsi_oversold):
                self.sell(sl=stop_loss, tp=take_profit)

def MACD(series, fast=12, slow=26, signal=9):
    """Return MACD indicator."""
    # Convert 'series' to pandas Series
    series = pd.Series(series)

    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd = fast_ema - slow_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd - signal_line

def ATR(high, low, close, n):
    """Compute Average True Range (ATR)"""
    # Convert input variables to pandas Series
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)

    hl = high - low
    hc = np.abs(high - close.shift())
    lc = np.abs(low - close.shift())
    tr = pd.DataFrame({'HL': hl, 'HC': hc, 'LC': lc}).max(axis=1)
    return tr.rolling(n).mean()

def RSI(series, n):
    """Compute Relative Strength Index (RSI)"""
    # Convert 'series' to pandas Series
    series = pd.Series(series)

    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=n).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Load your data here
data = pd.read_csv("historical-data/1d/BTC-USD-1d-2016.csv", sep=',')
data = data.drop(columns=['Unnamed: 6'])
data = dropna(data)
data['Time'] = pd.to_datetime(data['Time'])
data = data.set_index('Time')

# Backtest
bt = Backtest(data, WaveletBollingerBandsStrategy, cash=100000, commission=.002)
stats = bt.run()
print(stats)

# Optional: Plotting
bt.plot()




