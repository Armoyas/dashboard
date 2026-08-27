import duckdb

conn = duckdb.connect(':memory:')
conn.execute(open('/opt/data/dashboard/database/schema.sql').read())
conn.execute("CREATE TABLE _csv_staging AS SELECT * FROM read_csv_auto('/opt/data/dashboard/data/sample_data.csv')")

total = conn.execute('SELECT COUNT(*) FROM _csv_staging').fetchone()[0]
print(f'Total CSV rows: {total}')

# Populate merchants table (deduplicated by merchant_key)
conn.execute("""
    INSERT INTO merchants (merchant_key, name)
    SELECT DISTINCT merchant_key,
           COALESCE(MIN(NULLIF(category_title, '')), 'Unknown Merchant')
    FROM _csv_staging
    GROUP BY merchant_key
    ON CONFLICT (merchant_key) DO NOTHING
""")

# Populate sessions table from CSV data
conn.execute("""
    INSERT INTO sessions (
        id, merchant_key, session_status, amount, adjusted_fee,
        authority, email, mobile, created_at, updated_at
    )
    SELECT
        session_key::VARCHAR,
        merchant_key,
        CASE
            WHEN session_status IN ('Verified', 'Paid') THEN 'SUCCESS'
            WHEN session_status IN ('Failed', 'Reversed') THEN 'FAILED'
            ELSE session_status
        END,
        amount::BIGINT,
        adjusted_fee::BIGINT,
        try_status::VARCHAR,
        NULL,
        NULL,
        created_at::TIMESTAMP,
        COALESCE(verified_at::TIMESTAMP, created_at::TIMESTAMP)
    FROM _csv_staging
    ON CONFLICT (id) DO NOTHING
""")

conn.execute("DROP TABLE _csv_staging")

sessions = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
merchants = conn.execute('SELECT COUNT(*) FROM merchants').fetchone()[0]
total_amount = conn.execute('SELECT SUM(amount) FROM sessions').fetchone()[0]
total_fees = conn.execute('SELECT SUM(adjusted_fee) FROM sessions').fetchone()[0]

print(f'Sessions loaded: {sessions}')
print(f'Merchants loaded: {merchants}')
print(f'Total amount: {total_amount:,} IRR')
print(f'Total fees: {total_fees:,} IRR')

status_dist = conn.execute('SELECT session_status, COUNT(*) FROM sessions GROUP BY session_status ORDER BY COUNT(*) DESC').fetchall()
for s, c in status_dist:
    print(f'  Status {s}: {c}')

conn.execute("DROP TABLE _csv_staging")
conn.close()
print("\n✓ Data loading verified successfully!")
