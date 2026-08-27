import os
import psycopg2
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

cursor.execute("SELECT COUNT(*) FROM addresses;")
count = cursor.fetchone()[0]

print(f"Addresses in database: {count}")

cursor.execute("""
    SELECT address_id, address, city, state, zip
    FROM addresses
    ORDER BY address_id;
""")

for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()