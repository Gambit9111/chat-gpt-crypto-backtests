import pandas as pd
from ta.utils import dropna

def clean_data(df, date_as_index=True) -> pd.DataFrame:
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
    # # change date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    # # reset index
    df = df.reset_index(drop=True)
    
    if date_as_index:
        # # set date as index
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
    return df

    



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