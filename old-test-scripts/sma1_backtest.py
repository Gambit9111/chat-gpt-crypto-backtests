import pandas as pd
from ta.utils import dropna
from backtesting import Strategy, Backtest
from backtesting.lib import crossover
from pathlib import Path
import json
import os

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
    n1 = 50
    n2 = 200
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
    
    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

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
        
        stats = bt.optimize(n1=range(10, 50, 10),
                            n2=range(50, 100, 10),
                            maximize='Equity Final [$]',
                            constraint=lambda param: param.n1 < param.n2)
        
        
        
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


# for file_path in Path(sideways_directory).glob('*.csv'):
#     print(f'Processing file: {file_path}')


# for file_path in Path(downtrend_directory).glob('*.csv'):
#     print(f'Processing file: {file_path}')
    
    
    

    # df = pd.read_csv(file_path, sep=',')
    # df = dropna(df)
    # df['Time'] = pd.to_datetime(df['Time'])
    # df = df.set_index('Time')

    # # Create and backtest the strategy
    # bt = Backtest(df, SmaCross, cash=100_000, commission=.002)
    # stats = bt.optimize(n1=range(5, 100, 5),
    #                     n2=range(10, 200, 5),
    #                     maximize='Equity Final [$]',
    #                     constraint=lambda param: param.n1 < param.n2)
    
    # # Save the backtest results to a new csv file
    # file_name = file_path.stem  # Use the input file name as the output file name
    # output_file_path = Path(output_directory) / f'{file_name}_backtest_results.csv'
    # stats._trades.to_csv(output_file_path, index=False)  # Assuming _trades attribute contains the results of the backtest

    # print(f'Backtest results saved to: {output_file_path}')