from functions import clean_data, load_csv_with_header_check
from pathlib import Path
import json
import os


# # File path
# file_path = "historical-data/1h/SANDUSDT_1h-2020.csv"

# df = load_csv_with_header_check(file_path)
# df = clean_data(df)

# # Display the first few rows of the dataframe
# print(df)



# input_directory = 'historical-data/1h'
# output_directory = 'backtest-results/1h'

# for file_path in Path(input_directory).glob('*.csv'):
#     print(f'Processing file: {file_path}')