import duckdb

conn = duckdb.connect('/opt/data/dashboard/database/debug_analytics.duckdb')

# Check if tables exist
tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()
print(f'Tables before schema: {tables}')

# Apply schema
schema_content = open('/opt/data/dashboard/database/schema.sql').read()
conn.execute(schema_content)
conn.commit()

# Check tables after
tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()
print(f'Tables after schema: {tables}')

# Check _IN_DOCKER detection
from pathlib import Path
print(f"Path '/app/database/schema.sql' exists: {Path('/app/database/schema.sql').exists()}")
print("This means _IN_DOCKER is False, using local paths")

conn.close()
import os
os.remove('/opt/data/dashboard/database/debug_analytics.duckdb')
