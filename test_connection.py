import sys
sys.path.insert(0, '/opt/data/dashboard/backend')
import os
os.environ['DATABASE_PATH'] = '/opt/data/dashboard/database/test_analytics.duckdb'

# Clean up any existing test DB
test_db = '/opt/data/dashboard/database/test_analytics.duckdb'
if os.path.exists(test_db):
    os.remove(test_db)

from api.database.connection import get_connection

conn = get_connection()

sessions = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
merchants = conn.execute('SELECT COUNT(*) FROM merchants').fetchone()[0]
total_amount = conn.execute('SELECT SUM(amount) FROM sessions').fetchone()[0]
total_fees = conn.execute('SELECT SUM(adjusted_fee) FROM sessions').fetchone()[0]

print(f'Sessions: {sessions}')
print(f'Merchants: {merchants}')
print(f'Total amount: {total_amount:,} IRR')
print(f'Total fees: {total_fees:,} IRR')
print('✓ get_connection() works with CSV data!')

conn.close()
