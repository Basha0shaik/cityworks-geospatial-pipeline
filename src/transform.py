import pandas as pd
import geopandas as gpd


INPUT_FILE = "data/processed/clean_addresses.csv"
OUTPUT_FILE = "data/processed/addresses_geospatial.csv"


print("=== CITYWORKS GEOSPATIAL TRANSFORMATION ===")
print()

# 1. Read validated address data
df = pd.read_csv(INPUT_FILE)

print("Records loaded:", len(df))

# 2. Convert latitude and longitude to numbers
df["latitude"] = pd.to_numeric(df["latitude"])
df["longitude"] = pd.to_numeric(df["longitude"])

# 3. Create a GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["longitude"],
        df["latitude"]
    ),
    crs="EPSG:4326"
)

# 4. Display information
print()
print("Coordinate Reference System:", gdf.crs)

print()
print("Sample geometries:")
print(gdf[["address_id", "latitude", "longitude", "geometry"]].head())

# 5. Save the transformed data
gdf.to_csv(OUTPUT_FILE, index=False)

print()
print("Geospatial transformation completed.")
print("Output:", OUTPUT_FILE)