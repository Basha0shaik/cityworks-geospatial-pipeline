import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}


def generate_climate_report():

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("=== CITYWORKS CLIMATE RISK REPORT ===")
    print()

    query = """
        SELECT
            z.risk_type,
            z.risk_level,
            COUNT(DISTINCT a.address_id) AS address_count
        FROM addresses a
        JOIN climate_risk_zones z
            ON ST_Intersects(a.geometry, z.geometry)
        GROUP BY
            z.risk_type,
            z.risk_level
        ORDER BY
            z.risk_type;
    """

    cursor.execute(query)

    results = cursor.fetchall()
    climate_count = len(results)

    print("Climate Risk Summary:")
    print()

    for risk_type, risk_level, address_count in results:
        print(
            f"{risk_type} | "
            f"{risk_level} | "
            f"{address_count} addresses"
        )

    print()

    insert_query = """
    INSERT INTO climate_risk_summary (
        summary_date,
        risk_type,
        risk_level,
        address_count
    )
    SELECT
        CURRENT_DATE,
        z.risk_type,
        z.risk_level,
        COUNT(DISTINCT a.address_id)
    FROM addresses a
    JOIN climate_risk_zones z
        ON ST_Intersects(a.geometry, z.geometry)
    GROUP BY
        z.risk_type,
        z.risk_level

    ON CONFLICT (summary_date, risk_type, risk_level)
    DO UPDATE SET
        address_count = EXCLUDED.address_count,
        created_at = CURRENT_TIMESTAMP;
"""

    cursor.execute(insert_query)

    conn.commit()

    print("Daily climate summary saved.")

    cursor.close()
    conn.close()

    print("Database connection closed.")
    print(f"PIPELINE_CLIMATE_COUNT={climate_count}")


if __name__ == "__main__":
    generate_climate_report()