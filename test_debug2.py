import sys
sys.path.insert(0, '/opt/data/dashboard/backend')
import os

# Set the same env vars
os.environ['DATABASE_PATH'] = '/opt/data/dashboard/database/test_analytics.duckdb'

from pathlib import Path
from api.database.connection import _IN_DOCKER, DATABASE_PATH, SCHEMA_PATH, DATA_FILE

print(f"_IN_DOCKER = {_IN_DOCKER}")
print(f"DATABASE_PATH = {DATABASE_PATH}")
print(f"SCHEMA_PATH = {SCHEMA_PATH}")
print(f"DATA_FILE = {DATA_FILE}")
print(f"SCHEMA_PATH exists: {Path(SCHEMA_PATH).exists()}")
print(f"DATA_FILE exists: {Path(DATA_FILE).exists()}")

# Check _init_schema behavior
import duckdb
conn = duckdb.connect(DATABASE_PATH)
tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()
print(f"Tables in DB: {tables}")

if tables:
    print("_init_schema() would return early (tables exist) - but there shouldn't be any!")
    # Check what tables are there
    for t in tables:
        cols = conn.execute(f"PRAGMA table_info('{t[0]}')").fetchall()
        print(f"  Table '{t[0]}' columns: {[c[1] for c in cols]}")
else:
    print("_init_schema() would apply schema")
    if Path(SCHEMA_PATH).exists():
        schema = Path(SCHEMA_PATH).read_text()
        conn.execute(schema)
        conn.commit()
        tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()
        print(f"Tables after schema: {tables}")
    else:
        print(f"Schema file not found at {SCHEMA_PATH}")

conn.close()
