import pandas as pd
from ta.utils import dropna
from backtesting import Backtest
from pathlib import Path
from binance.spot import Spot
import json
import os
import time


def clean_data(file_path) -> pd.DataFrame:
    # Drop rows with any NaN or NaT values
    # drop unnamed column
    df = pd.read_csv(file_path, sep=',')
    try:
        df = df.drop(columns=['Unnamed: 6'])
    except:
        pass
    df = dropna(df)
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    # # set date as index
    # # change date to datetime
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    # Remove rows with NaT (Not a Time) values resulting from unconvertible date-time formats
    df = df.dropna(subset=['Time'])
    # Set 'Date' as index
    df = df.set_index('Time')
        
    
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Volume'] = df['Volume'].astype(float)
    
    return df

def get_period_from_csv(df, start_date, end_date):    
    period_data = df.loc[start_date:end_date]
    return period_data

def get_data(binance_client: Spot, symbol: str, interval: str, limit: int) -> pd.DataFrame:
    df = pd.DataFrame(binance_client.klines(symbol=symbol, interval=interval, limit=limit))
    df = df.iloc[:, :9]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_av', 'Trades']

    # drop unnecessary columns
    df = df.drop(['Close_time', 'Quote_av', 'Trades'], axis=1)

    # convert to datetime
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')

    # set index
    df = df.set_index('Time')
    # convert to float
    df = df.astype(float)

    return df

def save_bt_json(json_file_name: str, symbol: str, timeframe: str, stats: dict) -> None:

    stats_symbol = symbol
    stats_timeframe = timeframe
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
        "symbol": str(stats_symbol),
        "timeframe": str(stats_timeframe),
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
    
    with open(json_file_name, 'w') as json_file:
        json.dump(stats_data, json_file, indent=4)
        
def single_backtest_start(file_path: str, start_date: str, end_date: str, strategy, params: dict, save_the_plot: bool, use_full_data: bool, maximize_func, constraint_func) -> None:
    
    #get data
    df = clean_data(file_path)
    
    # get period
    if not use_full_data:
        df = get_period_from_csv(df, start_date, end_date)
    
    #start the backtest
    if save_the_plot:
        df = df.reset_index(drop=False)
    
    bt = Backtest(df, strategy, cash=100000, commission=.002, exclusive_orders=True)
    stats = bt.optimize(**params, maximize=maximize_func, constraint=constraint_func)
    print(stats)
    print(stats._strategy)
    
    
    file_path_str = str(file_path)  # Convert PosixPath object to a string
    timeframe = os.path.basename(os.path.dirname(file_path_str))
    html_dir = 'flask-chart-view/chart-html-files/' + timeframe + '/'
    json_dir = 'flask-chart-view/json-bt-results/' + timeframe + '/'
    symbol = file_path_str.split("/")[-1].split("-")[0]
    
    print(html_dir)
    print(json_dir)
    print(symbol)
    
    
    html_file_name = html_dir + symbol + '-USDT - ' + str(stats._strategy) + '.html'
    json_file_name = json_dir + symbol + '-USDT - ' + str(stats._strategy) + '.json'

    if save_the_plot:
        bt.plot(filename=html_file_name)
    
    save_bt_json(json_file_name, symbol, timeframe, stats)