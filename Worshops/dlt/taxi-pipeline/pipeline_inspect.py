import duckdb
from pathlib import Path


def main() -> None:
    db_path = Path("taxi_pipeline.duckdb")
    print("DB exists:", db_path.exists())

    conn = duckdb.connect(str(db_path))

    print("\n-- Tables --")
    tables = [row[0] for row in conn.execute("SHOW TABLES").fetchall()]
    for t in tables:
        print(t)

    # Prefer nyc_taxi_trips if present, otherwise fall back to taxi_trips
    trips_table = None
    for name in ("nyc_taxi_trips", "taxi_trips"):
        if name in tables:
            trips_table = name
            break

    print("\nTrips table:", trips_table)

    if trips_table:
        print(f"\n-- Schema for {trips_table} --")
        schema = conn.execute(f"PRAGMA table_info({trips_table})").fetchall()
        for cid, name, dtype, notnull, dflt, pk in schema:
            print(
                f"{name}\t{dtype}\tNOT NULL={bool(notnull)}\tPK={bool(pk)}"
            )

        print("\n-- Row count --")
        total_rows = conn.execute(
            f"SELECT COUNT(*) FROM {trips_table}"
        ).fetchone()[0]
        print("rows:", total_rows)

        print("\n-- Date range tpep_pickup_datetime --")
        min_ts, max_ts = conn.execute(
            f"""
            SELECT
                MIN(tpep_pickup_datetime),
                MAX(tpep_pickup_datetime)
            FROM {trips_table}
            """
        ).fetchone()
        print("min, max:", min_ts, max_ts)

        print("\n-- % credit card payments --")
        pct_cc = conn.execute(
            f"""
            SELECT
                100.0 * SUM(CASE WHEN payment_type = 'Credit Card' THEN 1 ELSE 0 END)
                / COUNT(*)
            FROM {trips_table}
            """
        ).fetchone()[0]
        print("pct_cc:", pct_cc)

        print("\n-- Total tip amount --")
        total_tip = conn.execute(
            f"SELECT SUM(tip_amount) FROM {trips_table}"
        ).fetchone()[0]
        print("total_tip:", total_tip)

    print("\n-- dlt metadata tables --")
    meta_counts: dict[str, int] = {}
    for t in tables:
        if t.startswith("dlt_"):
            meta_counts[t] = conn.execute(
                f"SELECT COUNT(*) FROM {t}"
            ).fetchone()[0]
    print(meta_counts)

    non_loaded_jobs = None
    if "dlt_load_jobs" in tables:
        non_loaded_jobs = conn.execute(
            """
            SELECT COUNT(*)
            FROM dlt_load_jobs
            WHERE status IS NOT NULL
              AND status <> 'loaded'
            """
        ).fetchone()[0]
        print("\nNon-loaded jobs in dlt_load_jobs:", non_loaded_jobs)

    conn.close()


if __name__ == "__main__":
    main()

