# CityWorks Geospatial Data Pipeline

A Python-based geospatial data engineering pipeline for validating address data, cleaning records, creating spatial geometries, loading data into PostgreSQL/PostGIS, performing climate-risk spatial analysis, and tracking pipeline executions.

## Pipeline Architecture

```text
Incoming CSV
     |
     v
  Extract
     |
     v
  Validate ---------> Rejected Records
     |
     v
   Clean
     |
     v
Geospatial Transform
     |
     v
PostgreSQL / PostGIS
     |
     v
Climate Risk Analysis
     |
     v
Pipeline Run Tracking
     |
     v
Run Summary

## Key Features

CSV address data ingestion
Data validation
Rejected-record handling
Data cleaning and standardization
Latitude/longitude to Point geometry conversion
EPSG:4326 spatial reference system
PostgreSQL integration
PostGIS spatial data storage
Duplicate-safe database loading
Spatial intersection using ST_Intersects
Climate-risk analysis
Daily climate-risk summaries
Pipeline execution tracking
Success and failure status tracking
Rejection-rate monitoring
Test-mode pipeline execution

## Technologies

Python
Pandas
GeoPandas
Shapely
PostgreSQL
PostGIS
psycopg2
python-dotenv
PowerShell
Visual Studio Code

## Project Structure

cityworks_geospatial_pipeline/
|
+-- data/
|   +-- incoming/
|   |   +-- addresses_2026-08-25.csv
|   |   +-- addresses_2026-08-26_test_bad.csv
|   |
|   +-- processed/
|   |   +-- addresses_geospatial.csv
|   |   +-- clean_addresses.csv
|   |   +-- valid_addresses.csv
|   |
|   +-- rejected/
|       +-- rejected_addresses.csv
|
+-- src/
|   +-- check_database.py
|   +-- check_geometry.py
|   +-- clean.py
|   +-- climate_report.py
|   +-- extract.py
|   +-- load.py
|   +-- pipeline_tracker.py
|   +-- run_pipeline.py
|   +-- transform.py
|   +-- validate.py
|
+-- check_pipeline_runs.py
+-- requirements.txt
+-- .gitignore
+-- README.md

## Pipeline Stages

1. Extract
The pipeline identifies the incoming address CSV file and prepares it for processing.
Example input:
data/incoming/addresses_2026-08-25.csv
Test input:
data/incoming/addresses_2026-08-26_test_bad.csv

2. Validate
The validation stage separates valid and rejected records.
Example test:
Records received: 8
Valid records: 5
Rejected records: 3
The pipeline calculates the rejection rate:
Rejection rate: 37.50%
A high rejection-rate alert is generated when the configured threshold is exceeded.
Example:
ALERT: HIGH REJECTION RATE DETECTED!
Rejection rate 37.50% exceeds threshold 20.00%
Valid records are written to:
data/processed/valid_addresses.csv
Rejected records are written to:
data/rejected/rejected_addresses.csv

3. Clean
Valid records are cleaned and standardized.
Output:
data/processed/clean_addresses.csv
Example cleaned records:
address_id        address          city      state   zip
1001100           Main street      New york  NY      10001
1002200           Broadway         New york  NY      10002
1003300           Madison Avenue   New york  NY      10003
1004400           Park Avenue      New york  NY      10004
1005500           5th Avenue       New york  NY      10005

4. Geospatial Transformation
Latitude and longitude values are converted into spatial Point geometries.
Coordinate Reference System:
EPSG:4326
Example:
POINT (-74.006 40.7128)
Output:
data/processed/addresses_geospatial.csv

5. PostGIS Loading
The transformed records are loaded into PostgreSQL/PostGIS.
Spatial geometry is created using:
ST_GeomFromText(..., 4326)
Duplicate address_id values are skipped using:
ON CONFLICT (address_id) DO NOTHING
Example:
Records to load: 5
Records inserted: 0
Records skipped: 5
This allows the pipeline to be safely re-run without creating duplicate addresses.

6. Climate Risk Analysis
The pipeline performs spatial intersection between address points and climate-risk zones.
Spatial analysis uses:
ST_Intersects()
Example result:
FLOOD | MEDIUM | 3 addresses
HEAT  | HIGH   | 3 addresses
The daily climate summary is stored in PostgreSQL.

7. Pipeline Run Tracking
Each pipeline execution receives a unique run ID.
The pipeline tracks:
run_id
started_at
completed_at
status
records_received
records_valid
records_rejected
rejection_rate
error_message
Example:
==================================================
CITYWORKS PIPELINE RUN SUMMARY
==================================================
Run ID:             21
Input file:         addresses_2026-08-26_test_bad.csv
Records received:   8
Records valid:      5
Records rejected:   3
Rejection rate:     37.50%
PostGis inserted:   0
PostGis skipped:    5
Climate categories: 2
Pipeline status:    SUCCESS
==================================================

Example Pipeline Execution
The test pipeline can be executed with:
python src/run_pipeline.py --test
Example output:
=== CITYWORKS GEOSPATIAL PIPELINE ===

Input file: addresses_2026-08-26_test_bad.csv
Records received: 8
Pipeline run started: 21

Records received: 8
Records valid: 5
Records rejected: 3

Rejection rate: 37.50%

Records to load: 5
Records inserted: 0
Records skipped: 5

FLOOD | MEDIUM | 3 addresses
HEAT  | HIGH   | 3 addresses

=== PIPELINE COMPLETED SUCCESSFULLY ===

Run ID: 21
Records received: 8
Records valid: 5
Records rejected: 3
Rejection rate: 37.50%
PostGis inserted: 0
PostGis skipped: 5
Climate categories: 2
Pipeline status: SUCCESS

## Database

The project uses PostgreSQL with the PostGIS extension.
The pipeline works with tables including:
addresses
climate_risk_zones
climate_risk_summary
pipeline_runs
PostGIS enables spatial storage and spatial SQL operations.

## Configuration

Database configuration is stored in a local .env file.
Example:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cityworks
DB_USER=postgres
DB_PASSWORD=your_password

## Security

The .env file contains database credentials and should never be committed to GitHub.
The .gitignore file should include:
.env
.venv/
__pycache__/
*.pyc

## Installation

1. Create a virtual environment
python -m venv .venv
2. Activate the virtual environment
.\.venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
4. Configure PostgreSQL/PostGIS
Create the required cityworks database and enable PostGIS.
CREATE EXTENSION postgis;
Configure the database connection in .env.
Running the Pipeline
Activate the virtual environment:
.\.venv\Scripts\Activate.ps1
Run the normal pipeline:
python src/run_pipeline.py
Run the test pipeline:
python src/run_pipeline.py --test
A successful execution produces:
=== PIPELINE COMPLETED SUCCESSFULLY ===
followed by the pipeline run summary.

## Verification

Check the database
python src/check_database.py
Check spatial geometries
python src/check_geometry.py
Check historical pipeline runs
python check_pipeline_runs.py
Example Test Run
The test dataset contains:
Records received: 8
Records valid: 5
Records rejected: 3
Therefore:
Rejection rate = 3 / 8 × 100
               = 37.50%
The pipeline detects the rejection rate as exceeding the configured threshold while continuing to process the valid records.
Example Climate Analysis
The spatial analysis produced:
FLOOD | MEDIUM | 3 addresses
HEAT  | HIGH   | 3 addresses
This demonstrates how PostGIS can be used to identify addresses located within climate-risk zones.

## Pipeline Monitoring

Pipeline executions are recorded in the pipeline_runs table.
Example historical execution:
Run ID: 21
Status: SUCCESS
Records received: 8
Records valid: 5
Records rejected: 3
Rejection rate: 37.50%
The pipeline also supports failure tracking through the pipeline tracker.

## Project Purpose

This project demonstrates practical geospatial data engineering by combining:
ETL processing
Data quality validation
Data cleaning
Spatial transformation
PostgreSQL/PostGIS
Spatial SQL
Geospatial analysis
Pipeline monitoring
Error handling
Reproducible execution

## Future Improvements

Potential future extensions include:
Automated scheduled execution
Cloud object storage
Cloud geospatial processing
REST API
Web GIS dashboard
Interactive climate-risk map
Automated data-quality reports
Structured application logging
Unit and integration testing
CI/CD
Docker deployment
Cloud deployment

## Status

Functional end-to-end geospatial data pipeline
The current implementation successfully demonstrates:
Extract
   ->
Validate
   ->
Clean
   ->
Transform
   ->
PostGIS Load
   ->
Climate Risk Analysis
   ->
Pipeline Tracking
   ->
Reporting

The project has been tested with both valid records and intentionally invalid records to demonstrate validation, rejection-rate monitoring, database loading, spatial analysis, and pipeline execution tracking.
