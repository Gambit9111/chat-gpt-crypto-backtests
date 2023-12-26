import backtesting
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import ta
from utils.functions2 import clean_data, get_period_from_csv, single_backtest_start
from pathlib import Path


def Donchian_hband_indicator(high, low, close, window):
    # Convert to pandas Series
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)

    donchian_channel = ta.volatility.DonchianChannel(high=high, low=low, close=close, window=window)
    return donchian_channel.donchian_channel_hband()

def Donchian_lband_indicator(high, low, close, window):
    # Convert to pandas Series
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)

    donchian_channel = ta.volatility.DonchianChannel(high=high, low=low, close=close, window=window)
    return donchian_channel.donchian_channel_lband()

def RSI_indicator(series, window):
    # Convert to pandas Series
    series = pd.Series(series)
    return ta.momentum.RSIIndicator(close=series, window=window).rsi()


class DCRSIStrategy(Strategy):
    donchian_window = 20
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30

    def init(self):
        self.dc_hband = self.I(Donchian_hband_indicator, self.data.High, self.data.Low, self.data.Close, self.donchian_window)
        self.dc_lband = self.I(Donchian_lband_indicator, self.data.High, self.data.Low, self.data.Close, self.donchian_window)
        self.rsi = self.I(RSI_indicator, self.data.Close, self.rsi_period)

    def next(self):
        is_buy_signal = crossover(self.data.Close, self.dc_hband) and self.rsi[-1] < self.rsi_overbought
        is_sell_signal = crossover(self.dc_lband, self.data.Close) or self.rsi[-1] > self.rsi_oversold

        # If a buy signal and no current long position, enter a long position
        if self.position.is_long:
            if is_sell_signal or self.rsi[-1] > self.rsi_overbought:
                self.position.close()

        # If already in a short position, check for conditions to exit
        elif self.position.is_short:
            if is_buy_signal or self.rsi[-1] < self.rsi_oversold:
                self.position.close()

        # If not in any position, check for entry signals
        else:
            if is_buy_signal:
                self.buy()
            elif is_sell_signal:
                self.sell()

#!---------------------------------------------------------------------------------

multi_params = {
    'donchian_window': range(18, 22, 2),
    'rsi_period': range(12, 16, 1),
    'rsi_overbought': range(60, 80, 5),
    'rsi_oversold': range(20, 40, 5)
}

single_params = {
    'donchian_window': [20],
    'rsi_period': [14],
    'rsi_overbought': [70],
    'rsi_oversold': [30]
}

params = {}

def maximize_func(series):
    # Optimization function can be tailored as needed
    return series['Max. Drawdown [%]']

def constraint_func(param):
    return lambda param: param.rsi_overbought > param.rsi_oversold

file_path = "historical-data/15min/BTC-USD-15m-2016.csv"
input_directories = ['historical-data/15min', 'historical-data/5min']
start_date = '2022-01-01'
end_date = '2024-10-31'

save_the_plot = True
use_full_data = False

bulk_backtest = False
optimize_params = False

if optimize_params:
    params = multi_params
else:
    params = single_params


if not bulk_backtest:
    single_backtest_start(file_path, start_date, end_date, DCRSIStrategy, params, save_the_plot, use_full_data, maximize_func, constraint_func)

if bulk_backtest:
    # # * multi file backtest controls
    for input_directory in input_directories:

        for file_path in Path(input_directory).glob('*.csv'):
            single_backtest_start(file_path, start_date, end_date, DCRSIStrategy, params, save_the_plot, use_full_data, maximize_func, constraint_func)