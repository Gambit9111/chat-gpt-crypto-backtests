import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import ta
from functions import clean_data, load_csv_with_header_check, single_backtest_start, multi_backtest_start
from pathlib import Path
import json
import os

#sl 0.02
#sma 27
#outperforms the market on ethusdt with a smalldrowdown


# Helper function for SMA indicator
def SMA_indicator(series, window):
    series = pd.Series(series)
    return ta.trend.SMAIndicator(series, window=window).sma_indicator()

# SMA crossover strategy with both long and short positions
class SMACrossoverStrategy(Strategy):
    # Risk management parameters
    stop_loss_percent = 0.02  # Stop loss as a fraction of entry price

    # Single SMA setting
    sma_period = 27  # SMA period
    
    def init(self):
        self.sma = self.I(SMA_indicator, self.data.Close, self.sma_period)

    def next(self):
        current_price = self.data.Close[-1]

        # Buy signal: Closing price crosses above the SMA
        if crossover(self.data.Close, self.sma):
            if self.position.is_short:
                self.position.close()  # Close short position if it exists
            entry_price = current_price
            stop_loss_price = entry_price * (1 - self.stop_loss_percent)
            self.buy(sl=stop_loss_price)

        # Sell signal: Closing price crosses below the SMA
        elif crossover(self.sma, self.data.Close):
            if self.position.is_long:
                self.position.close()  # Close long position if it exists
            entry_price = current_price
            stop_loss_price = entry_price * (1 + self.stop_loss_percent)
            self.sell(sl=stop_loss_price)

# params = {
#     'stop_loss_percent': [0.03, 0.06, 0.09, 0.12, 0.15, 0.18, 0.21, 0.25, 0.27, 0.29],  # Example: 0.02 (2%)
#     'sma_period': [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],  # Example: 27
# }

params = {
    'stop_loss_percent': [i / 100 for i in range(1, 21, 1)],
    'sma_period': [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
}


# Load your data here
file_path = "historical-data/1d/ETHUSDT_d-2017.csv"
save_the_plot = True
multi_backtest = True

def optim_func(series):
    # Optimization function can be tailored as needed
    return series['Max. Drawdown [%]']

# Multi file backtest controls
input_directory = 'historical-data/1d'
output_directory = 'flask-chart-view/json-bt-results/1d'

if multi_backtest:
    # Multiple file backtest
    for file_path in Path(input_directory).glob('*.csv'):
        try:
            multi_backtest_start(file_path, SMACrossoverStrategy, params, output_directory, optim_func, save_the_plot)
        except Exception as e:
            print(e)
            continue
else:
    # Single file backtest
    single_backtest_start(file_path, SMACrossoverStrategy, params, save_the_plot, optim_func)
