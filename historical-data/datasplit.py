import pandas as pd
from ta.utils import dropna

# Read the original csv file
df = pd.read_csv('15min/full/SOL-USD-15m-2021.csv', parse_dates=['Time'])
df = df.drop('Unnamed: 6', axis=1) # Drop the 'Unnamed: 6' column
df = dropna(df)

symbol = 'SOL'
trend = 'Sideways'
timeframe = '15m'

# Set the start and end dates
start_date = '2023-10-09'
end_date = '2023-12-23'

# Filter the data based on the date range
filtered_data = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)]

# Save the filtered data to a new csv file
filtered_data.to_csv(f'{symbol}-{timeframe}-{trend}-{start_date}-{end_date}.csv', index=False)