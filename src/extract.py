import pandas as pd

# Path to the incoming CSV file
file_path = "data/incoming/addresses_2026-08-25.csv"

# Read the CSV
df = pd.read_csv(file_path)

# Display basic information
print("=== CITYWORKS ADDRESS PIPELINE ===")
print()

print("Number of records:", len(df))

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 records:")
print(df.head())