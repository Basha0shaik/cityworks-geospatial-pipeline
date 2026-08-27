import pandas as pd


INPUT_FILE = "data/processed/valid_addresses.csv"
OUTPUT_FILE = "data/processed/clean_addresses.csv"


print("=== CITYWORKS DATA CLEANING ===")
print()

# Read validated data
df = pd.read_csv(INPUT_FILE)

print("Records loaded:", len(df))


# ---------------------------------------
# 1. Clean text fields
# ---------------------------------------

text_columns = [
    "address",
    "city",
    "state",
    "zip"
]

for column in text_columns:
    df[column] = df[column].astype(str).str.strip()


# ---------------------------------------
# 2. Clean address IDs
# ---------------------------------------

df["address_id"] = (
    df["address_id"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.strip()
)


# ---------------------------------------
# 3. Convert coordinates to numbers
# ---------------------------------------

df["latitude"] = pd.to_numeric(
    df["latitude"],
    errors="coerce"
)

df["longitude"] = pd.to_numeric(
    df["longitude"],
    errors="coerce"
)


# ---------------------------------------
# 4. Display cleaned data
# ---------------------------------------

print()
print("Cleaned records:")
print(
    df[
        [
            "address_id",
            "address",
            "city",
            "state",
            "zip",
            "latitude",
            "longitude"
        ]
    ].to_string(index=False)
)


# ---------------------------------------
# 5. Save cleaned data
# ---------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

print()
print("Cleaning completed.")
print("Output:", OUTPUT_FILE)