import pandas as pd
from ta.utils import dropna
from backtesting import Strategy, Backtest
from backtesting.lib import crossover
from pathlib import Path
import json
import os
import pandas_ta as ta

# Define the SMA function and SmaCross class here (as in the provided code)

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    upper_bound = 70
    lower_bound = 30
    rsi_window = 14

    
    def init(self):
        self.rsi = self.I(ta.rsi, pd.Series(self.data.Close), self.rsi_window)
    
    def next(self):
        if crossover(self.rsi, self.upper_bound):
            self.position.close()
        elif crossover(self.lower_bound, self.rsi):
            self.buy()


# Directory containing the csv files
directories = ['historical-data/15min/uptrend/',
               'historical-data/15min/sideways/',
               'historical-data/15min/downtrend/']

output_directory = 'backtest-results/'

for directory in directories:
# Iterate through each csv file in the input directory
    for file_path in Path(directory).glob('*.csv'):
        print(f'Processing file: {file_path}')
        
        df = pd.read_csv(file_path, sep=',')
        df = dropna(df)
        df['Time'] = pd.to_datetime(df['Time'])
        df = df.set_index('Time')
        
        bt = Backtest(df, SmaCross, cash=100_000, commission=.002)
        
        stats = bt.optimize(upper_bound = range(50,85,5),
                            lower_bound = range(15,45,5),
                            maximize='Equity Final [$]',
        )
        
        
        
        stats_start = stats['Start']
        stats_end = stats['End']
        stats_duration = stats['Duration']
        stats_exposure_time = stats['Exposure Time [%]']
        stats_equity_final = stats['Equity Final [$]']
        stats_equity_peak = stats['Equity Peak [$]']
        stats_return_percentage = stats['Return [%]']
        stats_buy_hold_return = stats['Buy & Hold Return [%]']
        stats_return_ann = stats['Return (Ann.) [%]']
        stats_volatility_ann = stats['Volatility (Ann.) [%]']
        stats_sharpe_ratio = stats['Sharpe Ratio']
        stats_sortino_ratio = stats['Sortino Ratio']
        stats_calmar_ratio = stats['Calmar Ratio']
        stats_max_drawdown = stats['Max. Drawdown [%]']
        stats_avg_drawdown = stats['Avg. Drawdown [%]']
        stats_max_drawdown_duration = stats['Max. Drawdown Duration']
        stats_avg_drawdown_duration = stats['Avg. Drawdown Duration']
        stats_trades = stats['# Trades']
        stats_win_rate = stats['Win Rate [%]']
        stats_best_trade = stats['Best Trade [%]']
        stats_worst_trade = stats['Worst Trade [%]']
        stats_avg_trade = stats['Avg. Trade [%]']
        stats_max_trade_duration = stats['Max. Trade Duration']
        stats_avg_trade_duration = stats['Avg. Trade Duration']
        stats_profit_factor = stats['Profit Factor']
        stats_expectancy = stats['Expectancy [%]']
        stats_sqn = stats['SQN']
        stats_strategy = stats['_strategy']

        stats_data = {
            "start": str(stats_start),
            "end": str(stats_end),
            "duration": str(stats_duration),
            "exposure_time": str(stats_exposure_time),
            "equity_final": str(stats_equity_final),
            "equity_peak": str(stats_equity_peak),
            "return_percentage": str(stats_return_percentage),
            "buy_hold_return": str(stats_buy_hold_return),
            "return_ann": str(stats_return_ann),
            "volatility_ann": str(stats_volatility_ann),
            "sharpe_ratio": str(stats_sharpe_ratio),
            "sortino_ratio": str(stats_sortino_ratio),
            "calmar_ratio": str(stats_calmar_ratio),
            "max_drawdown": str(stats_max_drawdown),
            "avg_drawdown": str(stats_avg_drawdown),
            "max_drawdown_duration": str(stats_max_drawdown_duration),
            "avg_drawdown_duration": str(stats_avg_drawdown_duration),
            "trades": str(stats_trades),
            "win_rate": str(stats_win_rate),
            "best_trade": str(stats_best_trade),
            "worst_trade": str(stats_worst_trade),
            "avg_trade": str(stats_avg_trade),
            "max_trade_duration": str(stats_max_trade_duration),
            "avg_trade_duration": str(stats_avg_trade_duration),
            "profit_factor": str(stats_profit_factor),
            "expectancy": str(stats_expectancy),
            "sqn": str(stats_sqn),
            "strategy": str(stats_strategy)
        }
        
        file_name = file_path.stem  # Use the input file name as the output file name
        
        sub_directory = None  # Sub-directory name
        
        if directory == 'historical-data/15min/uptrend/':
            sub_directory = 'uptrend'
        elif directory == 'historical-data/15min/sideways/':
            sub_directory = 'sideways'
        elif directory == 'historical-data/15min/downtrend/':
            sub_directory = 'downtrend'
            
        output_file_path = Path(output_directory) / sub_directory / f'{file_name}_backtest_results.json'

        # Create the sub-directory if it doesn't exist
        os.makedirs(output_file_path.parent, exist_ok=True)

        with open(output_file_path, 'w') as json_file:
            json.dump(stats_data, json_file, indent=4)