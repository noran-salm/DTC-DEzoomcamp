# 🚕 NYC Taxi Data Pipeline

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![dlt](https://img.shields.io/badge/dlt-1.0%2B-orange)](https://dlthub.com)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.0%2B-yellow)](https://duckdb.org)
[![Marimo](https://img.shields.io/badge/Marimo-0.20%2B-purple)](https://marimo.io)

End-to-end data pipeline using **dlt** to ingest NYC taxi data into **DuckDB**, analyzed through an interactive **Marimo** dashboard with Plotly visualizations.

---

## 📁 Project Structure

```
06-dlt-pipeline/
├── taxi_pipeline.py      # dlt ingestion pipeline
├── taxi_analysis.py      # Marimo analytics dashboard
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Tool | Role |
|---|---|---|
| Pipeline | dlt | Ingestion & orchestration |
| Database | DuckDB | Local analytics storage |
| Notebook | Marimo | Interactive dashboard |
| Visualization | Plotly | Charts & maps |
| Processing | Pandas, NumPy | Data manipulation |

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the pipeline

```bash
python taxi_pipeline.py
```

Creates `taxi_pipeline.duckdb` with a `taxi_trips` table loaded from the dlt NYC taxi source.

### 3. Launch the dashboard

```bash
marimo edit taxi_analysis.py
```

---

## 📊 Dashboard Sections

| Section | Charts | Key Metrics |
|---|---|---|
| 💳 **Payment Analysis** | Donut · Grouped bar · Tip rate | Trip mix, avg fare, tip rate |
| 🛣️ **Distance Analysis** | Histogram · Quartile bar | Mean, median, P75, P95 |
| 📈 **Time Series** | Bar + 7-day MA · Day×Hour heatmap | Daily volume, demand patterns |
| 💰 **Fare & Tip** | Density scatter · Tip % histogram | Correlation, zero-tip rate |
| 👥 **Passengers** | Volume bar · Multi-metric line | Avg fare/distance/tip per group |
| 🗺️ **Pickup Map** | Geo scatter (fare-coloured) | Spatial demand distribution |

> All charts are fully interactive — hover, zoom, pan, and range-select supported.

---

## ⚙️ Pipeline Configuration

### Write disposition options

```python
@dlt.resource(
    name="taxi_trips",
    write_disposition="replace"   # replace | append | merge
)
def taxi_trips_resource():
    ...
```

### Incremental loading

```python
@dlt.resource(
    primary_key="_dlt_id",
    write_disposition="append"
)
def taxi_trips_incremental(
    updated_at=dlt.sources.incremental("trip_pickup_date_time")
):
    ...
```

---

## 🔍 Sample Queries

```python
import duckdb

conn = duckdb.connect("taxi_pipeline.duckdb")

# Basic stats
conn.execute("""
    SELECT
        COUNT(*)            AS total_trips,
        AVG(fare_amt)       AS avg_fare,
        AVG(tip_amt)        AS avg_tip,
        AVG(trip_distance)  AS avg_distance
    FROM taxi_pipeline.taxi_trips
""").df()

# Hourly demand heatmap data
conn.execute("""
    SELECT
        DAYOFWEEK(trip_pickup_date_time) AS dow,
        HOUR(trip_pickup_date_time)      AS hour,
        COUNT(*)                         AS trips
    FROM taxi_pipeline.taxi_trips
    GROUP BY dow, hour
    ORDER BY dow, hour
""").df()

# Payment type breakdown
conn.execute("""
    SELECT
        payment_type,
        COUNT(*)            AS trips,
        AVG(fare_amt)       AS avg_fare,
        AVG(tip_amt)        AS avg_tip,
        100.0 * AVG(tip_amt / NULLIF(fare_amt, 0)) AS tip_pct
    FROM taxi_pipeline.taxi_trips
    WHERE payment_type IS NOT NULL
    GROUP BY payment_type
    ORDER BY trips DESC
""").df()
```

---

## 🧪 Debugging

```bash
# Inspect pipeline state
dlt pipeline taxi_pipeline info

# Show loaded tables
dlt pipeline taxi_pipeline show

# Trace last run
dlt pipeline taxi_pipeline trace
```

---

## 📚 Resources

- [dlt Documentation](https://dlthub.com/docs)
- [DuckDB Documentation](https://duckdb.org/docs)
- [Marimo Documentation](https://docs.marimo.io)
- [Plotly Python Docs](https://plotly.com/python)

---

## 🤝 Contributing

Contributions welcome — new data sources, additional analyses, statistical tests, or ML models. Open an issue or submit a PR.

---

*Part of the [DTC DE Zoomcamp](https://github.com/noran-salm/DTC-DEzoomcamp) · Workshop 1*