import pandas as pd
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
import os


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "addresses_geospatial.csv"

# Load .env from project root
load_dotenv(PROJECT_ROOT / ".env")


# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


# --------------------------------------------------
# VALIDATE DATABASE CONFIGURATION
# --------------------------------------------------

required_vars = [
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
]

missing_vars = [
    var for var in required_vars
    if not os.getenv(var)
]

if missing_vars:
    raise RuntimeError(
        f"Missing database environment variables: {', '.join(missing_vars)}"
    )


# --------------------------------------------------
# START LOAD
# --------------------------------------------------

print("=== CITYWORKS POSTGIS LOAD ===")


# 1. Read transformed CSV
df = pd.read_csv(INPUT_FILE)

print(f"Records to load: {len(df)}")


# 2. Connect to PostgreSQL
conn = psycopg2.connect(**DB_CONFIG)

cursor = conn.cursor()

print("Connected to PostgreSQL.")


# --------------------------------------------------
# 3. INSERT RECORDS
# --------------------------------------------------

insert_sql = """
    INSERT INTO addresses
    (
        address_id,
        address,
        city,
        state,
        zip,
        latitude,
        longitude,
        geometry
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s,
        ST_GeomFromText(%s, 4326)
    )
    ON CONFLICT (address_id) DO NOTHING
"""


try:
    inserted_count = 0
    skipped_count = 0

    for _, row in df.iterrows():

        geometry_wkt = row["geometry"]

        cursor.execute(
            insert_sql,
            (
                str(row["address_id"]),
                row["address"],
                row["city"],
                row["state"],
                str(row["zip"]),
                float(row["latitude"]),
                float(row["longitude"]),
                geometry_wkt
            )
        )
        if cursor.rowcount == 1:
            inserted_count += 1
        else:
            skipped_count += 1

    # Save changes
    conn.commit()

    #print(f"Successfully loaded {len(df)} records.")
    print(f"Records inserted: {inserted_count}")
    print(f"Records skipped: {skipped_count}")

except Exception:

    conn.rollback()

    print("ERROR: Database transaction rolled back.")

    raise


finally:

    cursor.close()
    conn.close()

    print("Database connection closed.")


print("PostGIS loading completed.")

print(f"PIPELINE_INSERTED={inserted_count}")
print(f"PIPELINE_SKIPPED={skipped_count}")