import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import ta
from ta.utils import dropna
from functions import clean_data, load_csv_with_header_check

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
    stop_loss_percent = 0.1  # Stop loss as a fraction of entry price
    take_profit_percent = 0.1  # Take profit as a fraction of entry price

    def init(self):
        self.sma_short = self.I(SMA_indicator, self.data.Close, 18)  # Short SMA (18 days)
        self.sma_long = self.I(SMA_indicator, self.data.Close, 183)  # Long SMA (183 days)
        self.sma_200_day = self.I(SMA_indicator, self.data.Close, 200*24)  # Long SMA (200 days)
        self.peak_equity = 0  # Track the highest portfolio value

    def next(self):
        self.peak_equity = max(self.peak_equity, self.equity)

        is_buy_signal = crossover(self.sma_short, self.sma_long)
        is_sell_signal = crossover(self.sma_long, self.sma_short)

        if is_buy_signal:
            self.position.close()
            entry_price = self.data.Close[-1]
            stop_loss_price = entry_price * (1 - self.stop_loss_percent)  # Stop price for a long position
            take_profit_price = entry_price * (1 + self.take_profit_percent)
            self.buy(sl=stop_loss_price, tp=take_profit_price)

        elif is_sell_signal:
            self.position.close()
            entry_price = self.data.Close[-1]
            stop_loss_price = entry_price * (1 + self.stop_loss_percent)  # Stop price for a short position
            take_profit_price = entry_price * (1 - self.take_profit_percent)  #
            self.sell(sl=stop_loss_price, tp=take_profit_price)

# Load your data here
file_path = "historical-data/1h/ACMUSDT_1h-2021.csv"
data = load_csv_with_header_check(file_path)
data = clean_data(data, True)

# Backtesting
bt = Backtest(data, SMACrossoverStrategy, cash=100000, commission=.002)

params = {
    'stop_loss_percent': [i / 10.0 for i in range(1, 10)],
    'take_profit_percent': [i / 10.0 for i in range(1, 10)]
}

def optim_func(series):
    
    # return series['Equity Final [$]'] / series['Max. Drawdown [%]']
    return series['Return [%]']

# Run optimization
opt_stats = bt.optimize(**params, maximize=optim_func)
print(opt_stats)
print(opt_stats._strategy)
bt.plot()