import duckdb

# Connect to the pipeline_pipeline database (the one with data)
conn = duckdb.connect("taxi_pipeline_pipeline.duckdb")

# See what tables exist
tables = conn.execute("SHOW TABLES").fetchall()
print("Tables in taxi_pipeline_pipeline.duckdb:")
for table in tables:
    print(f"  📊 {table[0]}")
    
    # Count rows in each table
    count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
    print(f"     Rows: {count:,}")

# If nyc_taxi_trips exists, answer the homework questions
try:
    # Question 1: Date range
    result1 = conn.execute("""
        SELECT 
            MIN(tpep_pickup_datetime) as start_date,
            MAX(tpep_pickup_datetime) as end_date
        FROM nyc_taxi_trips
    """).fetchone()
    print(f"\n📅 Date range: {result1[0]} to {result1[1]}")
    
    # Question 2: Credit card %
    result2 = conn.execute("""
        SELECT 
            ROUND(100.0 * SUM(CASE WHEN payment_type = 'Credit Card' THEN 1 ELSE 0 END) / COUNT(*), 2)
        FROM nyc_taxi_trips
    """).fetchone()[0]
    print(f"💳 Credit card: {result2}%")
    
    # Question 3: Total tips
    result3 = conn.execute("SELECT ROUND(SUM(tip_amount), 2) FROM nyc_taxi_trips").fetchone()[0]
    print(f"💰 Total tips: ${result3}")
    
except Exception as e:
    print(f"\n❌ Couldn't find nyc_taxi_trips: {e}")

conn.close()