import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

cursor.execute("""
    SELECT
        address_id,
        address,
        ST_AsText(geometry) AS geometry,
        ST_SRID(geometry) AS srid
    FROM addresses
    ORDER BY address_id;
""")

rows = cursor.fetchall()

print("\n=== POSTGIS GEOMETRY CHECK ===")

for row in rows:
    print(row)

cursor.close()
conn.close()

print("\nGeometry verification completed.")