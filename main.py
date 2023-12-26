import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import ta
from utils.functions2 import single_backtest_start
from pathlib import Path
import json
import os




# Helper function for SMA indicator
def SMA_indicator(series, window):
    series = pd.Series(series)
    return ta.trend.SMAIndicator(series, window=window).sma_indicator()

# Helper function for EMA indicator
def EMA_indicator(series, window):
    series = pd.Series(series)
    return ta.trend.EMAIndicator(series, window=window).ema_indicator()

# SMA crossover strategy with single position management and stop-loss
class SMACrossoverStrategy(Strategy):
    # Risk management parameters
    stop_loss_percent = 0.02  # Stop loss as a fraction of entry price
    
    sma_short = 15
    sma_long = 196
    ema_day = 1535

    def init(self):
        self.sma_short = self.I(SMA_indicator, self.data.Close, self.sma_short)  # Short SMA (18 days)
        self.sma_long = self.I(SMA_indicator, self.data.Close, self.sma_long)  # Long SMA (183 days)
        self.ema_day = self.I(EMA_indicator, self.data.Close, self.ema_day)  # Long EMA (200 days)

    def next(self):
        current_price = self.data.Close[-1]

        is_buy_signal = crossover(self.sma_short, self.sma_long)
        is_sell_signal = crossover(self.sma_long, self.sma_short)

        if is_buy_signal:
            if self.position.is_short:
                self.position.close()  # Close short position if it exists
            elif current_price > self.ema_day[-1]:
                self.position.close()  # Close any existing long position before opening a new one
                entry_price = self.data.Close[-1]
                stop_loss_price = entry_price * (1 - self.stop_loss_percent)  # Stop price for a long position
                # self.buy(sl=stop_loss_price)
                self.buy()

        elif is_sell_signal:
            if self.position.is_long:
                self.position.close()  # Close long position if it exists
            elif current_price < self.ema_day[-1]:
                self.position.close()  # Close any existing short position before opening a new one
                entry_price = self.data.Close[-1]
                stop_loss_price = entry_price * (1 + self.stop_loss_percent)  # Stop price for a short position
                # self.sell(sl=stop_loss_price)
                self.sell()


multi_params = {
    # 'stop_loss_percent': [0.02, 0.04, 0.06, 0.08, 0.1],
    'sma_short': range(15, 90, 15),
    'sma_long': range(50, 200, 15),
    'ema_day': range(25, 300, 25)
}

single_params = {
    # 'stop_loss_percent': [0.02, 0.04, 0.06, 0.08, 0.1],
    'sma_short': [30],  # Example: 10, 15, 20, 25, 30
    'sma_long': [160],  # Example: 150, 160, ..., 220
    'ema_day': [300]  # Example: 4800 (200 days), 5040 (210 days), ..., 7200 (300 days)
}

params = {}

def maximize_func(series):
    # Optimization function can be tailored as needed
    return series['Max. Drawdown [%]']

def constraint_func(param):
    return lambda param: param.sma_short < param.sma_long

file_path = "historical-data/15min/BTC-USD-15m-2016.csv"
input_directories = ['historical-data/15min', 'historical-data/5min']
start_date = '2022-01-01'
end_date = '2024-10-31'

save_the_plot = True
use_full_data = False
optimize_params = True

bulk_backtest = True

if optimize_params:
    params = multi_params
else:
    params = single_params


if not bulk_backtest:
    single_backtest_start(file_path, start_date, end_date, SMACrossoverStrategy, params, save_the_plot, use_full_data, maximize_func, constraint_func)

if bulk_backtest:
    # # * multi file backtest controls
    for input_directory in input_directories:

        for file_path in Path(input_directory).glob('*.csv'):
            single_backtest_start(file_path, start_date, end_date, SMACrossoverStrategy, params, save_the_plot, use_full_data, maximize_func, constraint_func)