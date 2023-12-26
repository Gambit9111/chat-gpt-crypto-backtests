import pandas as pd
from binance.spot import Spot
import os
import time
from utils.functions2 import clean_data, get_data


binance_client = Spot()
# Directory containing the CSV files
directories = ["historical-data/5min/", "historical-data/15min"]
for directory in directories:
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