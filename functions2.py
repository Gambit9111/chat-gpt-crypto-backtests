import pandas as pd
from ta.utils import dropna
from backtesting import Backtest
from pathlib import Path
from binance.spot import Spot
import json
import os
import time

def clean_data(df, date_as_index) -> pd.DataFrame:
    # Drop rows with any NaN or NaT values
    # drop unnamed column
    try:
        df = df.drop(columns=['Unnamed: 6'])
    except:
        pass
    df = dropna(df)
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    
    if date_as_index:
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

#!----------------------


binance_client = Spot()
# Directory containing the CSV files
directory = "historical-data/5min/"

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        
        try:
        
            file_path = os.path.join(directory, filename)
            
            print(f"Reading {file_path}...")

            # Extract symbol ticker from filename
            symbol_ticker = filename.split('-')[0]
            print(f"Symbol ticker: {symbol_ticker}")

            print(f"Updating DataFrame for {symbol_ticker}...")
            # Read and clean historical data
            df = pd.read_csv(file_path, sep=',')
            df = clean_data(df, True)
            print(df)

            # # Fetch and clean current data from Binance using extracted symbol ticker
            binance_df = get_data(binance_client, f'{symbol_ticker}USDT', '5m', 1000)
            # binance_df = clean_data(binance_df, True)
            
            # print(binance_df)

            # # Find the last datetime in df
            last_datetime = df.index[-1]
            
            print(f"Last datetime in DataFrame: {last_datetime}")

            # # Filter binance_df to include only new data after last_datetime
            new_data = binance_df[binance_df.index > last_datetime]
            
            # print(new_data)

            # # Append new data to df
            updated_df = df._append(new_data)
            
            print(updated_df)

            # Save the updated dataframe to the original CSV file
            updated_df.to_csv(file_path, sep=',', index=True)

            # Print confirmation
            print(f"Updated DataFrame for {symbol_ticker} has been saved to {file_path}")
            
            time.sleep(5)
        
        except Exception as e:
            print(e)
            continue

print("All files have been updated.")

# binance_client = Spot()

# file_path = "historical-data/5min/AAVE-USD-5m-2021.csv"
# symbol_ticker = "AAVE"
# df = pd.read_csv(file_path, sep=',')

# df = clean_data(df, True)
# print(df)

# binance_df = get_data(binance_client, f'{symbol_ticker}USDT', '5m', 1000)
# print(binance_df)
# # # Find the last datetime in df
# last_datetime = df.index[-1]
# new_data = binance_df[binance_df.index > last_datetime]
# updated_df = df._append(new_data)
# updated_df.to_csv(file_path, sep=',', index=True)
# print(f"Updated DataFrame for {symbol_ticker} has been saved to {file_path}")