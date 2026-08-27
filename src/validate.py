import pandas as pd
import sys


DEFAULT_INPUT_FILE = "data/incoming/addresses_2026-08-25.csv"

if len(sys.argv) > 1:
    INPUT_FILE = sys.argv[1]
else:
    INPUT_FILE = DEFAULT_INPUT_FILE
VALID_OUTPUT = "data/processed/valid_addresses.csv"
REJECTED_OUTPUT = "data/rejected/rejected_addresses.csv"


REQUIRED_COLUMNS = [
    "address_id",
    "address",
    "city",
    "state",
    "zip",
    "latitude",
    "longitude"
]


def validate_records(df):
    valid_records = []
    rejected_records = []

    for index, row in df.iterrows():

        errors = []

        # Check required fields
        for column in REQUIRED_COLUMNS:
            if pd.isna(row[column]) or str(row[column]).strip() == "":
                errors.append(f"Missing {column}")

        # Check latitude
        if pd.notna(row["latitude"]):
            try:
                latitude = float(row["latitude"])

                if latitude < -90 or latitude > 90:
                    errors.append("Invalid latitude")

            except ValueError:
                errors.append("Invalid latitude")

        # Check longitude
        if pd.notna(row["longitude"]):
            try:
                longitude = float(row["longitude"])

                if longitude < -180 or longitude > 180:
                    errors.append("Invalid longitude")

            except ValueError:
                errors.append("Invalid longitude")

        # Store valid or rejected record
        if errors:
            rejected_row = row.copy()
            rejected_row["rejection_reason"] = "; ".join(errors)

            rejected_records.append(rejected_row)

        else:
            valid_records.append(row)

    return (
        pd.DataFrame(valid_records),
        pd.DataFrame(rejected_records)
    )


# ---------------------------------------
# MAIN PIPELINE
# ---------------------------------------

print("=== CITYWORKS VALIDATION PIPELINE ===")
print()

# Read incoming data
df = pd.read_csv(INPUT_FILE)

print("Incoming records:", len(df))

# Validate records
valid_df, rejected_df = validate_records(df)

# Save valid records
valid_df.to_csv(VALID_OUTPUT, index=False)

# Save rejected records
rejected_df.to_csv(REJECTED_OUTPUT, index=False)

print("Valid records:", len(valid_df))
print("Rejected records:", len(rejected_df))

print()
print("Valid output:")
print(VALID_OUTPUT)

print()
print("Rejected output:")
print(REJECTED_OUTPUT)

print()
print("Validation completed.")