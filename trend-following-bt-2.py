import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import ta
from ta.utils import dropna

# Helper function for SMA indicator
def SMA_indicator(series, window):
    series = pd.Series(series)
    return ta.trend.SMAIndicator(series, window=window).sma_indicator()

# SMA crossover strategy implementation
class SMACrossoverStrategy(Strategy):
    def init(self):
        # Setting up the short and long simple moving averages
        self.sma_short = self.I(SMA_indicator, self.data.Close, 18)  # Short SMA (18 days)
        self.sma_long = self.I(SMA_indicator, self.data.Close, 183)  # Long SMA (183 days)

    def next(self):
        # Buy if the short SMA crosses above the long SMA
        if crossover(self.sma_short, self.sma_long):
            self.buy()

        # Sell if the short SMA crosses below the long SMA
        elif crossover(self.sma_long, self.sma_short):
            self.sell()

# Load your data here
data = pd.read_csv("historical-data/1d/BTC-USD-1d-2016.csv", sep=',')
data = data.drop(columns=['Unnamed: 6'])
data = dropna(data)
data['Time'] = pd.to_datetime(data['Time'])
data = data.set_index('Time')

# Backtesting
bt = Backtest(data, SMACrossoverStrategy, cash=100000, commission=.002)
stats = bt.run()
print(stats)
bt.plot()

