import pandas as pd
from ta.utils import dropna
from backtesting import Backtest
from pathlib import Path
import json
import os

def clean_data(df, date_as_index) -> pd.DataFrame:
    # Drop rows with any NaN or NaT values
    df = dropna(df)
    # Drop duplicates
    df = df.drop_duplicates()
    # get the volume label
    symbol = df.iloc[0, 2]
    symbol = symbol.replace("USDT", "")
    volume_label = 'Volume ' + symbol
    # Select needed columns
    df = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close', volume_label]]
    # reverse the order of the dataframe
    df = df.iloc[::-1]
    # # reset index
    df = df.reset_index(drop=True)
    
    if not date_as_index:
        # # set date as index
        # # change date to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # Remove rows with NaT (Not a Time) values resulting from unconvertible date-time formats
        df = df.dropna(subset=['Date'])
        # Set 'Date' as index
        df = df.set_index('Date')
    
    # # change open, high, low, close, volume to float
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df[volume_label] = df[volume_label].astype(float)
    
    # calculate volume change
    # df['Volume Change'] = df[volume_label].pct_change()
    # df['200_day_MA'] = df['Close'].rolling(window=200*24).mean()
    return df, symbol

    



# # Load your data here
# df = pd.read_csv("historical-data/1d/SOLUSDT_d-2020.csv", sep=',')

# df = clean_data(df)

# print(df)


def load_csv_with_header_check(file_path):
    # Open the file and read the first line
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()

    # Check if the first line contains column names
    # This is a basic check assuming column names are typical data field names
    # Adjust the logic here if your criteria for detecting an advertisement are different
    if all(x.isalpha() or x in [',', ' '] for x in first_line):
        # If the first line is a header
        data = pd.read_csv(file_path, sep=',')
    else:
        # If the first line is an advertisement, set header to the second line
        data = pd.read_csv(file_path, sep=',', header=1)

    return data

# # File path
# file_path = "historical-data/1d/DOGEUSDT_d-2019.csv"

# # Load the data
# data = load_csv_with_header_check(file_path)

# # Display the first few rows of the dataframe
# print(data)



def multi_backtest_start(file_path, strategy, params, output_directory, optim_func):

    print(f'Processing file: {file_path}')

    data = load_csv_with_header_check(file_path)
    data, symbol = clean_data(data, True)

    # # Backtesting
    bt = Backtest(data, strategy, cash=100000, commission=.002)

    # # params = {
    # #     'stop_loss_percent': [0.2, 0.25, 0.3],
    # #     'sma_short': range(14, 16, 1),  # Example: 10, 15, 20, 25, 30
    # #     'sma_long': range(194, 198, 1),  # Example: 150, 160, ..., 220
    # #     'sma_day': range(1520, 1600, 10)  # Example: 4800 (200 days), 5040 (210 days), ..., 7200 (300 days)
    # # }

    # Run optimization
    stats = bt.optimize(**params, maximize=optim_func)

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
    
    file_name = file_path.stem
    output_file_path = Path(output_directory) / f'{file_name}_backtest_results.json'

    # Create the sub-directory if it doesn't exist
    os.makedirs(output_file_path.parent, exist_ok=True)

    with open(output_file_path, 'w') as json_file:
        json.dump(stats_data, json_file, indent=4)
        
        
def single_backtest_start(file_path, strategy, params, save_the_plot, optim_func):
    data = load_csv_with_header_check(file_path)
    data, symbol = clean_data(data, save_the_plot)
    
    # print(data)
    # print(symbol)

    # # # # Backtesting
    bt = Backtest(data, strategy, cash=100000, commission=.002)

    # # # Run optimization
    opt_stats = bt.optimize(**params, maximize=optim_func)

    file_dir = 'flask-chart-view/chart-html-files/'
    file_name = file_dir + symbol + '-USDT - ' + str(opt_stats._strategy) + '.html'

    if save_the_plot:
        bt.plot(filename=file_name, resample="12H")
    else:
        print(opt_stats)










# params = {
#     'stop_loss_percent': [0.25],
#     'sma_short': [15],
#     'sma_long': [196],
#     'sma_day': [1535]
# }

# # # params = {
# # #     'stop_loss_percent': [0.2, 0.25, 0.3],
# # #     'sma_short': range(14, 16, 1),  # Example: 10, 15, 20, 25, 30
# # #     'sma_long': range(194, 198, 1),  # Example: 150, 160, ..., 220
# # #     'sma_day': range(1520, 1600, 10)  # Example: 4800 (200 days), 5040 (210 days), ..., 7200 (300 days)
# # # }


# def optim_func(series):
    
#     # return series['Equity Final [$]'] / series['Max. Drawdown [%]']
#     return series['Return [%]']

# #! single file backtest controls
# save_the_plot = True
# single_file_path = "historical-data/1h/ADAUSDT_1h-2018.csv"

# # * multi file backtest controls
# multi_backtest = False
# input_directory = 'historical-data/1h'
# output_directory = 'backtest-results/1h'

# if multi_backtest:
#     # * Multiple file backtest
#     for file_path in Path(input_directory).glob('*.csv'):
#         try:
#             multi_backtest_start(file_path, SMACrossoverStrategy, params, output_directory, optim_func)
#         except Exception as e:
#             print(e)
#             continue

# else:
#     # ! Single file backtest
#     single_backtest_start(single_file_path, SMACrossoverStrategy, params, save_the_plot, optim_func)