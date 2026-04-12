# 🐍 Data Platforms Module using Bruin 

## What is Bruin?
Bruin is a data pipeline tool that helps you build, run, and manage data workflows. Think of it as an orchestrator for your data tasks!

---

## 📦 Installation

```bash
# Install Bruin
curl -L https://bruin-data.io/install.sh | bash

# Verify installation
bruin --version
```

---

## 🏗️ Project Structure

A basic Bruin project looks like this:

```
my-taxi-pipeline/
├── .bruin.yml              # Config file (connections, environments)
└── pipeline/               # Main pipeline folder
    ├── pipeline.yml        # Pipeline definition (name, schedule, vars)
    └── assets/             # Your code goes here!
        ├── ingestion/       # Raw data
        ├── staging/         # Cleaned data  
        └── reports/         # Final outputs
```

---

## 🚀 Common Commands

| Command | What it does |
|---------|--------------|
| `bruin init my-project` | Create new project |
| `bruin validate` | Check if everything is correct |
| `bruin run` | Run the pipeline |
| `bruin lineage` | Show asset dependencies |
| `bruin query` | Query your database |

---

## 📝 Asset Types

### Python Asset (`trips.py`)
```python
"""@bruin
name: ingestion.trips
type: python
connection: duckdb-default

materialization:
  type: table
  strategy: append
@bruin"""

import pandas as pd

def materialize():
    # Your code here
    df = pd.read_parquet("data.parquet")
    return df  # Bruin saves this to DB
```

### SQL Asset (`trips.sql`)
```sql
/* @bruin
name: staging.trips
type: duckdb.sql
depends:
  - ingestion.trips

materialization:
  type: table
  strategy: time_interval
  incremental_key: pickup_datetime
@bruin */

SELECT * FROM ingestion.trips
WHERE pickup_datetime >= '{{ start_datetime }}'
```

---

## 🔄 Materialization Strategies

| Strategy | What it does | When to use |
|----------|--------------|-------------|
| `table` | Drop & recreate entire table | Small data, full rebuilds |
| `append` | Add new rows only | Log data, never changes |
| `time_interval` | Delete & insert for date range | Time-partitioned data (NYC taxi!) |
| `merge` | Upsert based on keys | Slowly changing dimensions |

---

## 🎯 Running the Pipeline

```bash
# First time run (creates tables)
bruin run --full-refresh

# Normal run (incremental)
bruin run

# Specific date range
bruin run --start-date 2023-01-01 --end-date 2023-01-31

# Override variables
bruin run --var 'taxi_types=["yellow"]'

# Run asset + everything that depends on it
bruin run --select ingestion.trips+
```

---

## ✅ Quality Checks

```yaml
columns:
  - name: pickup_datetime
    type: timestamp
    checks:
      - name: not_null        # No NULLs allowed!
      - name: unique          # All values different
      
  - name: fare_amount
    type: double
    checks:
      - name: positive        # Must be > 0
      - name: non_negative     # Must be >= 0
```

---

## 🔍 Useful Tips

1. **Always validate first:** `bruin validate`
2. **Use `--full-refresh` for first runs**
3. **Check lineage:** `bruin lineage assets/file.py`
4. **Environment vars:** Bruin passes `BRUIN_START_DATE`, `BRUIN_END_DATE`
5. **Variables:** Access via `BRUIN_VARS` env

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No tasks to run" | Check `pipeline.yml` has assets defined |
| "Connection not defined" | Add `connection:` to asset metadata |
| Asset not found | Check file path in `pipeline.yml` |
| Wrong date range | Use ISO format: `2023-01-01` |

---

## 📚 Example: NYC Taxi Pipeline

```
ingestion.trips (Python) ──┐
                            ├── staging.trips (SQL) ──┐
ingestion.payment_lookup ──┘                           ├── reports.trips (SQL)
```

**Run it:**
```bash
cd my-taxi-pipeline/pipeline
bruin validate
bruin run --start-date 2023-01-01 --end-date 2023-01-31
```

---

## 🎓 Key Concepts

- **Asset** = A task (Python/SQL file)
- **Pipeline** = Collection of assets
- **Materialization** = How data is saved
- **Lineage** = Dependencies between assets
- **Incremental** = Process only new/changed data

---

## 💡 Pro Tips

- Start with small date ranges for testing
- Use `time_interval` for time-series data
- Add quality checks to catch bad data early
- Check lineage before modifying assets
- Keep assets small and focused

---

*Happy Building! 🚀*