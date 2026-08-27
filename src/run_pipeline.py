import subprocess
from pathlib import Path
import pandas as pd
import psycopg2
import os
import sys

from dotenv import load_dotenv

from pipeline_tracker import start_run, complete_run, fail_run


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

INCOMING_DIR = PROJECT_ROOT / "data" / "incoming"
VALID_FILE = PROJECT_ROOT / "data" / "processed" / "valid_addresses.csv"
REJECTION_THRESHOLD = 20.0


def run_script(script_name, args=None):
    print(f"\n--- Running {script_name} ---")

    command = [
        sys.executable,
        str(PROJECT_ROOT / "src" / script_name)
    ]

    if args:
        command.extend(args)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True
    )

    # Show the script output in the terminal
    if result.stdout:
        print(result.stdout, end="")

    if result.stderr:
        print(result.stderr, end="")

    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed.")

    print(f"--- {script_name} completed ---")

    return result.stdout


def find_input_file(test_mode=False):

    if test_mode:
        test_file = PROJECT_ROOT / "data" / "incoming" / "addresses_2026-08-26_test_bad.csv"

        if not test_file.exists():
            raise FileNotFoundError(
                f"Test input file not found: {test_file}"
            )

        return test_file

    files = [
        f
        for f in INCOMING_DIR.glob("addresses_*.csv")
        if "_test_bad" not in f.name
    ]

    if not files:
        raise FileNotFoundError(
            "No valid incoming addresses CSV found."
        )

    return max(files, key=lambda f: f.stat().st_mtime)


def print_run_summary(
    run_id,
    input_file,
    records_received,
    records_valid,
    records_rejected,
    rejection_rate,
    inserted_count,
    skipped_count,
    climate_count
):
    print("\n")
    print("=" * 50)
    print("CITYWORKS PIPELINE RUN SUMMARY")
    print("=" * 50)

    print(f"Run ID:             {run_id}")
    print(f"Input file:         {input_file.name}")
    print(f"Records received:   {records_received}")
    print(f"Records valid:      {records_valid}")
    print(f"Records rejected:   {records_rejected}")
    print(f"Rejection rate:     {rejection_rate:.2f}%")
    print(f"PostGis inserted: {inserted_count}")
    print(f"PostGis skipped: {skipped_count}")
    print(f"Climate categories: {climate_count}")
    print("Pipeline status:    SUCCESS")

    print("=" * 50)


def main():

    print("\n=== CITYWORKS GEOSPATIAL PIPELINE ===")
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"

    # --------------------------------------------------
    # 1. Find incoming file
    # --------------------------------------------------

    input_file = find_input_file(test_mode)

    incoming_df = pd.read_csv(input_file)

    records_received = len(incoming_df)

    print(f"\nInput file: {input_file.name}")
    print(f"Records received: {records_received}")

    # --------------------------------------------------
    # 2. Start pipeline tracking
    # --------------------------------------------------

    run_id = start_run(records_received)

    print(f"Pipeline run started: {run_id}")

    try:

        # --------------------------------------------------
        # 3. Validate
        # --------------------------------------------------

        run_script("validate.py", [str(input_file)])
        

        valid_df = pd.read_csv(VALID_FILE)

        records_valid = len(valid_df)

        # Rejected = incoming - valid
        records_rejected = records_received - records_valid
        if records_received > 0:
            rejection_rate = (
                records_rejected / records_received
            ) * 100
        else:
            rejection_rate = 0.0
        print(f"Rejection rate: {rejection_rate:.2f}%")
        if rejection_rate > REJECTION_THRESHOLD:
            print("\n ALERT: HIGH REJECTION RATE DETECTED!")
            print(
                f"Rejection rate {rejection_rate:.2f}% "
                f"exceeds threshold {REJECTION_THRESHOLD:.2f}%"
            )

        print(f"\nValid records: {records_valid}")
        print(f"Rejected records: {records_rejected}")

        # --------------------------------------------------
        # 4. Clean
        # --------------------------------------------------

        run_script("clean.py")

        # --------------------------------------------------
        # 5. Geospatial transformation
        # --------------------------------------------------

        run_script("transform.py")

        # --------------------------------------------------
        # 6. Load into PostGIS
        # --------------------------------------------------

        load_output = run_script("load.py")

        inserted_count = 0
        skipped_count = 0

        for line in load_output.splitlines():
            if line.startswith("PIPELINE_INSERTED="):
                inserted_count = int(line.split("=")[1])

            elif line.startswith("PIPELINE_SKIPPED="):
                skipped_count = int(line.split("=")[1])

        # 7.Generate climate-risk summary
        climate_output = run_script("climate_report.py")

        climate_count = 0

        for line in climate_output.splitlines():
            if line.startswith("PIPELINE_CLIMATE_COUNT="):
                climate_count = int(line.split("=")[1])

        # --------------------------------------------------
        # 8. Mark successful
        # --------------------------------------------------

        complete_run(
            run_id,
            records_valid=records_valid,
            records_rejected=records_rejected,
            rejection_rate=rejection_rate
        )

        print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")

        print(f"Run ID: {run_id}")
        print(f"Records received: {records_received}")
        print(f"Records valid: {records_valid}")
        print(f"Records rejected: {records_rejected}")
        print_run_summary(
    run_id=run_id,
    input_file=input_file,
    records_received=records_received,
    records_valid=records_valid,
    records_rejected=records_rejected,
    rejection_rate=rejection_rate,
    inserted_count=inserted_count,
    skipped_count=skipped_count,
    climate_count=climate_count
)

    except Exception as e:

        fail_run(run_id)

        print("\n=== PIPELINE FAILED ===")

        print(f"Run ID: {run_id}")
        print(f"Error: {e}")

        raise


if __name__ == "__main__":
    main()