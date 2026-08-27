import duckdb

conn = duckdb.connect(':memory:')
conn.execute("CREATE TABLE _csv_raw AS SELECT * FROM read_csv_auto('/opt/data/dashboard/data/sample_data.csv')")
cols = conn.execute("PRAGMA table_info(_csv_raw)").fetchall()
print("CSV Columns:")
for c in cols:
    print(f"  {c[1]} ({c[2]})")

sample = conn.execute("SELECT * FROM _csv_raw LIMIT 2").fetchall()
print("\nSample data:")
for row in sample:
    print(f"  {row}")

statuses = conn.execute("SELECT DISTINCT session_status FROM _csv_raw LIMIT 10").fetchall()
print(f"\nDistinct session_status values: {statuses}")

try_statuses = conn.execute("SELECT DISTINCT try_status FROM _csv_raw LIMIT 10").fetchall()
print(f"Distinct try_status values: {try_statuses}")
