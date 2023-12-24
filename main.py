import backtesting
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import ta


def Donchian_hband_indicator(series, window):
    series = pd.Series(series)
    return ta.volatility.DonchianChannel(series, window=window).donchian_channel_hband()

def Donchian_lband_indicator(series, window):
    series = pd.Series(series)
    return ta.volatility.DonchianChannel(series, window=window).donchian_channel_lband()

def RSI_indicator(series, window):
    series = pd.Series(series)
    return ta.momentum.RSIIndicator(close=series, window=window).rsi()


class DCRSIStrategy(Strategy):
    
    donchian_window = 20
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30

    def init(self):
        self.dc_hband = self.I(Donchian_hband_indicator, self.data.Close, self.donchian_window)
        self.dc_lband = self.I(Donchian_lband_indicator, self.data.Close, self.donchian_window)
        self.rsi = self.I(RSI_indicator, self.data.Close, self.rsi_period)

    def next(self):
        
        current_price = self.data.Close[-1]
        is_buy_signal = crossover(self.data.Close, self.dc_hband) and self.rsi[-1] < self.rsi_overbought
        is_sell_signal = crossover(self.dc_lband, self.data.Close) or self.rsi[-1] > self.rsi_oversold
        
        if is_buy_signal:
            if self.position.is_short:
                self.position.close()
            entry_price = self.data.Close[-1]
            self.buy()
        
        elif is_sell_signal:
            if self.position.is_long:
                self.position.close()
            entry_price = self.data.Close[-1]
            self.sell()


params = {
    'donchian_window': range(10, 30, 2),
    'rsi_period': range(10, 20, 2),
    'rsi_overbought': range(50, 90, 5),
    'rsi_oversold': range(10, 40, 5)
}

