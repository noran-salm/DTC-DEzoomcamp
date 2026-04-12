# 🚖 Bruin Pipeline Homework  
**Data Engineering Zoomcamp**  
**Student:** Nouran  

---

## 📋 Quick Answers Summary

| # | Question | Answer |
|---|----------|--------|
| 1 | Pipeline Structure | `.bruin.yml` + `pipeline/` with `pipeline.yml` & `assets/` |
| 2 | Best Materialization | `time_interval` |
| 3 | Override Variable | `bruin run --var 'taxi_types=["yellow"]'` |
| 4 | Run with Dependencies | `bruin run --select ingestion.trips+` |
| 5 | Quality Check | `name: not_null` |
| 6 | Visualize Lineage | `bruin lineage` |
| 7 | First-time Run | `--full-refresh` |

---

## 📖 Question 1: Pipeline Structure

**What files/folders does Bruin NEED to work?**

```
your-project/
├── .bruin.yml          # 👈 MUST have (connections & settings)
└── pipeline/           # 👈 MUST have
    ├── pipeline.yml    # 👈 MUST have (defines your pipeline)
    └── assets/         # 👈 MUST have (your code goes here)
        ├── ingestion/
        ├── staging/
        └── reports/
```

✅ **Correct:** `.bruin.yml and pipeline/ with pipeline.yml and assets/`

*Without this structure, Bruin won't find your pipeline!*

---

## 📖 Question 2: Materialization Strategies

**I have taxi data organized by month. I want to delete & re-insert data for a specific time period. Which strategy?**

```sql
/* @bruin
materialization:
  type: table
  strategy: time_interval    ✅ THIS ONE!
  incremental_key: pickup_datetime
*/
```

✅ **Correct:** `time_interval`

**Why?**
- Deletes ONLY the dates you're processing
- Inserts fresh data for those same dates
- Leaves other months untouched

**Think of it like:** "Clean January's data and replace it with fresh January data"

❌ `append` = just add more rows (creates duplicates)  
❌ `replace` = throw away EVERYTHING (too heavy)  
❌ `view` = doesn't store data at all

---

## 📖 Question 3: Pipeline Variables

**In `pipeline.yml` I have:**
```yaml
variables:
  taxi_types:
    type: array
    default: ["yellow", "green"]  # both by default
```

**I want ONLY yellow taxis. What command?**

✅ **Correct:** 
```bash
bruin run --var 'taxi_types=["yellow"]'
```

**Why this syntax?**
- It's an **array** → needs JSON format `["yellow"]`
- Must use `--var` flag
- Quotes matter!

**In your Python code:**
```python
import json, os
vars = json.loads(os.environ.get("BRUIN_VARS", "{}"))
taxi_types = vars.get("taxi_types")  # 👈 gets ["yellow"]
```

❌ `--taxi-types yellow` → wrong flag  
❌ `--var taxi_types=yellow` → wrong format (string vs array)

---

## 📖 Question 4: Running with Dependencies

**I fixed a bug in `ingestion/trips.py`. Now I want to run it AND everything that depends on it. What command?**

✅ **Correct:**
```bash
bruin run --select ingestion.trips+
```

**The `+` is magic!** It means:
```
ingestion.trips
       ↓
staging.trips (depends on ingestion)
       ↓
reports.trips_report (depends on staging)
```

**Without `+`** → runs only `ingestion.trips`  
**With `+`** → runs the whole chain

❌ `--all` → not a Bruin flag  
❌ `--downstream` → not correct syntax

---

## 📖 Question 5: Quality Checks

**I want to make sure `pickup_datetime` NEVER has NULL values. What check?**

✅ **Correct:** `name: not_null`

```yaml
columns:
  - name: pickup_datetime
    type: timestamp
    checks:
      - name: not_null   # 👈 This!
```

**Other checks (wrong for this case):**

| Check | What it does | Why not here |
|-------|--------------|--------------|
| `unique` | No duplicates | Timestamps CAN repeat |
| `positive` | Value > 0 | For numbers, not dates |
| `accepted_values` | Must be in list | Wrong syntax/purpose |

---

## 📖 Question 6: Lineage and Dependencies

**I want to SEE how my assets connect (dependency graph). What command?**

✅ **Correct:** `bruin lineage`

```bash
# See lineage for one asset
bruin lineage assets/ingestion/trips.py

# See full pipeline lineage  
bruin lineage .
```

**What you'll see:**
```
ingestion.trips ──┐
                  ├── staging.trips ──┐
ingestion.payment ──┘                   ├── reports.trips
```

**Proof it works (from your terminal):**
```bash
bruin lineage
# 👉 Asks for asset path (it EXISTS!)

bruin graph  
# 👉 "No help topic for 'graph'" (doesn't exist!)
```

---

## 📖 Question 7: First-Time Run

**I'm running this pipeline for the FIRST time on a new database. How do I create everything from scratch?**

✅ **Correct:** `--full-refresh`

```bash
bruin run --full-refresh
```

**What this does:**
- Drops existing tables (if any)
- Creates new tables with correct schema
- Runs ALL assets completely
- Perfect for: first run, schema changes, or fixing corrupted data

**After first run, you can run normally:**
```bash
bruin run  # 👈 incremental, only processes new data
```

❌ `--create` → not a Bruin flag  
❌ `--init` → not a Bruin flag  
❌ `--truncate` → empties tables but doesn't rebuild schema

---

## 🧪 Quick Verification (from YOUR terminal)

```bash
# Check Question 6 - lineage EXISTS
bruin lineage
# Output: "Please give an asset path..." ✅

# Check Question 6 - graph DOESN'T exist
bruin graph  
# Output: "No help topic for 'graph'" ✅
```

---

## 🎯 Key Takeaways

1. **Structure matters** - Bruin needs the right folders!
2. **`time_interval`** is your friend for time-based data
3. **Arrays need JSON format** when overriding
4. **`+` runs downstream** dependencies
5. **`not_null`** keeps bad data out
6. **`bruin lineage`** shows you the big picture
7. **`--full-refresh`** starts fresh

---

*Happy Data Engineering! 🚀*