from functions import clean_data, load_csv_with_header_check


# File path
file_path = "historical-data/1h/SANDUSDT_1h-2020.csv"

df = load_csv_with_header_check(file_path)
df = clean_data(df)

# Display the first few rows of the dataframe
print(df)