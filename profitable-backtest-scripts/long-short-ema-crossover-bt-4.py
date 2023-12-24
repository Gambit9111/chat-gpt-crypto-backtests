import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import ta
from functions import clean_data, load_csv_with_header_check, single_backtest_start, multi_backtest_start
from pathlib import Path
import json
import os


# VET 1h 60/70
# GALA 1h 75/135
# MATIC 1h 20/60
# XRP 1h 140/150
# ADA 1h 60/150

# Helper function for EMA indicator
def EMA_indicator(series, window):
    series = pd.Series(series)
    return ta.trend.EMAIndicator(series, window=window).ema_indicator()

# EMA crossover strategy with position flipping and stop-loss
class EMACrossoverStrategy(Strategy):
    # Risk management parameters
    stop_loss_percent = 0.02  # Stop loss as a fraction of entry price
    
    ema_short = 15
    ema_long = 196

    def init(self):
        self.ema_short = self.I(EMA_indicator, self.data.Close, self.ema_short)  # Short EMA
        self.ema_long = self.I(EMA_indicator, self.data.Close, self.ema_long)  # Long EMA

    def next(self):
        current_price = self.data.Close[-1]
        is_buy_signal = crossover(self.ema_short, self.ema_long)
        is_sell_signal = crossover(self.ema_long, self.ema_short)

        if is_buy_signal:
            if self.position.is_short:
                self.position.close()  # Close short position if it exists
            entry_price = self.data.Close[-1]
            stop_loss_price = entry_price * (1 - self.stop_loss_percent)  # Stop price for a long position
            self.buy()

        elif is_sell_signal:
            if self.position.is_long:
                self.position.close()  # Close long position if it exists
            entry_price = self.data.Close[-1]
            stop_loss_price = entry_price * (1 + self.stop_loss_percent)  # Stop price for a short position
            self.sell()

params = {
    # 'stop_loss_percent': [0.25],
    'ema_short': range(5, 200, 5),  # Example: 10, 15, 20, 25, 30
    'ema_long': range(5, 200, 5),  # Example: 150, 160, ..., 220
}

# Load your data here
file_path = "historical-data/1d/ETHUSDT_d-2017.csv"
save_the_plot = True
multi_backtest = True

def optim_func(series):
    # Optimization function can be tailored as needed
    return series['Max. Drawdown [%]']

# Multi file backtest controls
input_directory = 'historical-data/1h'
output_directory = 'flask-chart-view/json-bt-results/1h'

if multi_backtest:
    # Multiple file backtest
    for file_path in Path(input_directory).glob('*.csv'):
        try:
            multi_backtest_start(file_path, EMACrossoverStrategy, params, output_directory, optim_func, save_the_plot)
        except Exception as e:
            print(e)
            continue
else:
    # Single file backtest
    single_backtest_start(file_path, EMACrossoverStrategy, params, save_the_plot, optim_func)
