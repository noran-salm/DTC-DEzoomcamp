import dlt


def main() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination="duckdb",
        dataset_name="taxi_data",
    )
    sql = pipeline.sql_client()
    sql.open_connection()
    conn = sql.native_connection

    print("-- Tables --")
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

    if not trips_table:
        sql.close_connection()
        return

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

    print("\n-- Date range trip_pickup_date_time --")
    min_ts, max_ts = conn.execute(
        f"""
        SELECT
            MIN(trip_pickup_date_time),
            MAX(trip_pickup_date_time)
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

    print("\n-- Total tip amount (tip_amt) --")
    total_tip = conn.execute(
        f"SELECT SUM(tip_amt) FROM {trips_table}"
    ).fetchone()[0]
    print("total_tip:", total_tip)

    print("\n-- dlt metadata tables --")
    meta = {}
    for t in tables:
        if t.startswith("_dlt_"):
            meta[t] = conn.execute(
                f"SELECT COUNT(*) FROM {t}"
            ).fetchone()[0]
    print(meta)

    if "_dlt_loads" in tables:
        print("\n_dlt_loads contents:")
        loads = conn.execute(
            "SELECT * FROM _dlt_loads"
        ).fetchall()
        for row in loads:
            print(row)

    sql.close_connection()


if __name__ == "__main__":
    main()

