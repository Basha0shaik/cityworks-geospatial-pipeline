import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def start_run(records_received):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO pipeline_runs
        (status, records_received, records_valid, records_rejected)
        VALUES (%s, %s, %s, %s)
        RETURNING run_id;
        """,
        ("RUNNING", records_received, 0, 0)
    )

    run_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return run_id


def complete_run(run_id, records_valid, records_rejected, rejection_rate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE pipeline_runs
        SET
            completed_at = CURRENT_TIMESTAMP,
            status = %s,
            records_valid = %s,
            records_rejected = %s,
            rejection_rate = %s
        WHERE run_id = %s;
        """,
        ("SUCCESS", records_valid, records_rejected, rejection_rate, run_id)
    )

    conn.commit()
    cur.close()
    conn.close()


def fail_run(run_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE pipeline_runs
        SET
            completed_at = CURRENT_TIMESTAMP,
            status = %s
        WHERE run_id = %s;
        """,
        ("FAILED", run_id)
    )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    print("=== PIPELINE TRACKER TEST ===")

    run_id = start_run(8)

    print(f"Pipeline run started: {run_id}")

    complete_run(
        run_id,
        records_valid=5,
        records_rejected=3,
        rejection_rate=37.50
    )

    print("Pipeline run completed successfully.")