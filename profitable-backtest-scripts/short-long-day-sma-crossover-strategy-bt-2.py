import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import ta
from functions import clean_data, load_csv_with_header_check, single_backtest_start, multi_backtest_start
from pathlib import Path
import json
import os

    # 'stop_loss_percent': [i / 10.0 for i in range(1, 10)],
    # 'take_profit_percent': [i / 10.0 for i in range(1, 10)]
    
    # does not outperform the market on bigger timeframes
    # ! outperforms the market on 1h timeframes on btc since 2018 and solana since 2020


# Helper function for SMA indicator
def SMA_indicator(series, window):
    series = pd.Series(series)
    return ta.trend.SMAIndicator(series, window=window).sma_indicator()

# SMA crossover strategy with single position management and stop-loss
class SMACrossoverStrategy(Strategy):
    # Risk management parameters
    stop_loss_percent = 0.25  # Stop loss as a fraction of entry price
    
    sma_short = 15
    sma_long = 196
    sma_day = 1535

    def init(self):
        self.sma_short = self.I(SMA_indicator, self.data.Close, self.sma_short)  # Short SMA (18 days)
        self.sma_long = self.I(SMA_indicator, self.data.Close, self.sma_long)  # Long SMA (183 days)
        self.sma_day = self.I(SMA_indicator, self.data.Close, self.sma_day)  # Long SMA (200 days)

    def next(self):
        current_price = self.data.Close[-1]

        is_buy_signal = crossover(self.sma_short, self.sma_long)
        is_sell_signal = crossover(self.sma_long, self.sma_short)

        if is_buy_signal:
            if self.position.is_short:
                self.position.close()  # Close short position if it exists
            elif current_price > self.sma_day[-1]:
                self.position.close()  # Close any existing long position before opening a new one
                entry_price = self.data.Close[-1]
                stop_loss_price = entry_price * (1 - self.stop_loss_percent)  # Stop price for a long position
                self.buy(sl=stop_loss_price)

        elif is_sell_signal:
            if self.position.is_long:
                self.position.close()  # Close long position if it exists
            elif current_price < self.sma_day[-1]:
                self.position.close()  # Close any existing short position before opening a new one
                entry_price = self.data.Close[-1]
                stop_loss_price = entry_price * (1 + self.stop_loss_percent)  # Stop price for a short position
                self.sell(sl=stop_loss_price)




params = {
    'stop_loss_percent': [0.25],
    'sma_short': [15],  # Example: 10, 15, 20, 25, 30
    'sma_long': [196],  # Example: 150, 160, ..., 220
    'sma_day': [1535]  # Example: 4800 (200 days), 5040 (210 days), ..., 7200 (300 days)
}


# Load your data here
file_path = "historical-data/1h/SOLUSDT_1h-2020.csv"
save_the_plot = False
multi_backtest = False

def optim_func(series):
    # return series['Equity Final [$]'] / series['Max. Drawdown [%]']
    return series['Return [%]']


# # * multi file backtest controls
input_directory = 'historical-data/1h'
output_directory = 'backtest-results/1h'

if multi_backtest:
    # * Multiple file backtest
    for file_path in Path(input_directory).glob('*.csv'):
        try:
            multi_backtest_start(file_path, SMACrossoverStrategy, params, output_directory, optim_func)
        except Exception as e:
            print(e)
            continue

else:
    #! Single file backtest
    single_backtest_start(file_path, SMACrossoverStrategy, params, save_the_plot, optim_func)



# data = load_csv_with_header_check(file_path)
# data, symbol = clean_data(data, False)

# # # Backtesting
# bt = Backtest(data, SMACrossoverStrategy, cash=100000, commission=.002)

# # stats = bt.run()
# # print(stats)

# # params = {
# #     'stop_loss_percent': [0.2, 0.25, 0.3],
# #     'sma_short': range(14, 16, 1),  # Example: 10, 15, 20, 25, 30
# #     'sma_long': range(194, 198, 1),  # Example: 150, 160, ..., 220
# #     'sma_day': range(1520, 1600, 10)  # Example: 4800 (200 days), 5040 (210 days), ..., 7200 (300 days)
# # }

# params = {
#     'stop_loss_percent': [0.25],
#     'sma_short': [15],  # Example: 10, 15, 20, 25, 30
#     'sma_long': [196],  # Example: 150, 160, ..., 220
#     'sma_day': [1535]  # Example: 4800 (200 days), 5040 (210 days), ..., 7200 (300 days)
# }

# def optim_func(series):
    
#     # return series['Equity Final [$]'] / series['Max. Drawdown [%]']
#     return series['Return [%]']

# # Run optimization
# opt_stats = bt.optimize(**params, maximize=optim_func)
# print(opt_stats)
# print(opt_stats._strategy)

# file_dir = 'flask-chart-view/chart-html-files/'
# file_name = file_dir + symbol + '-USDT - ' + str(opt_stats._strategy) + '.html'

# bt.plot(filename=file_name, resample="12H")