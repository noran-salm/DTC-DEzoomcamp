"""@bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: pickup_datetime
    type: timestamp
    description: "When the meter was engaged"
  - name: dropoff_datetime
    type: timestamp
    description: "When the meter was disengaged"
  - name: pickup_location_id
    type: integer
  - name: dropoff_location_id
    type: integer
  - name: fare_amount
    type: double
  - name: payment_type
    type: integer
  - name: taxi_type
    type: string
  - name: extracted_at
    type: timestamp
@bruin"""

import os
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

def month_starts(start_ts: pd.Timestamp, end_ts: pd.Timestamp):
    return pd.date_range(start=start_ts.normalize(), end=end_ts.normalize(), freq="MS")

def download(url: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

def materialize():
    # Get environment variables
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date)
    
    # Get taxi types from variables
    vars_json = json.loads(os.environ.get("BRUIN_VARS", "{}"))
    taxi_types = vars_json.get("taxi_types", ["yellow"])

    # Cache directory
    cache_dir = Path(os.environ.get("BRUIN_TMP_DIR", "/tmp")) / "nyc_taxi"
    extracted_at = datetime.now(timezone.utc)

    dfs = []
    for taxi_type in taxi_types:
        for m in month_starts(start_ts, end_ts):
            ym = f"{m.year}-{m.month:02d}"
            fname = f"{taxi_type}_tripdata_{ym}.parquet"
            url = f"{BASE_URL}/{fname}"
            local = cache_dir / taxi_type / fname

            try:
                download(url, local)
                df = pd.read_parquet(local)
                
                # Handle different column names for different taxi types
                pickup_col = 'tpep_pickup_datetime' if 'tpep_pickup_datetime' in df.columns else 'lpep_pickup_datetime' if 'lpep_pickup_datetime' in df.columns else 'pickup_datetime'
                dropoff_col = 'tpep_dropoff_datetime' if 'tpep_dropoff_datetime' in df.columns else 'lpep_dropoff_datetime' if 'lpep_dropoff_datetime' in df.columns else 'dropoff_datetime'
                
                df["pickup_datetime"] = pd.to_datetime(df[pickup_col], utc=True, errors="coerce")
                df["dropoff_datetime"] = pd.to_datetime(df[dropoff_col], utc=True, errors="coerce")
                
                # Filter to date range
                df = df[(df["pickup_datetime"] >= start_ts) & (df["pickup_datetime"] <= end_ts)]
                
                # Add metadata columns
                df["taxi_type"] = taxi_type
                df["extracted_at"] = extracted_at
                
                # Select and rename columns
                df = df.rename(columns={
                    'PULocationID': 'pickup_location_id',
                    'DOLocationID': 'dropoff_location_id',
                    'payment_type': 'payment_type'
                })
                
                # Keep only relevant columns
                cols_to_keep = ['pickup_datetime', 'dropoff_datetime', 'pickup_location_id', 
                              'dropoff_location_id', 'fare_amount', 'payment_type', 
                              'taxi_type', 'extracted_at']
                available_cols = [col for col in cols_to_keep if col in df.columns]
                df = df[available_cols]
                
                dfs.append(df)
                print(f"Downloaded and processed {fname} with {len(df)} rows")
                
            except Exception as e:
                print(f"Error processing {fname}: {e}")
                continue

    if not dfs:
        return pd.DataFrame(columns=["pickup_datetime", "dropoff_datetime", "pickup_location_id", 
                                   "dropoff_location_id", "fare_amount", "payment_type", 
                                   "taxi_type", "extracted_at"])

    final_df = pd.concat(dfs, ignore_index=True)
    print(f"Total rows processed: {len(final_df)}")
    return final_df