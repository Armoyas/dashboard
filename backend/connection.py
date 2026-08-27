import os
import duckdb

DATABASE_PATH = os.environ.get("DATABASE_PATH", "/app/database/analytics.duckdb")

def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    con = duckdb.connect(DATABASE_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS merchants (
            merchant_key VARCHAR PRIMARY KEY,
            name VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            merchant_key VARCHAR,
            session_status VARCHAR,
            amount BIGINT,
            adjusted_fee BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    count = con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    if count == 0:
        con.execute("""
            INSERT INTO merchants VALUES 
            (\x27merchant_zarrin_01\x27, \x27Tech Store\x27, CURRENT_TIMESTAMP),
            (\x27merchant_zarrin_02\x27, \x27Online Academy\x27, CURRENT_TIMESTAMP);

            INSERT INTO transactions VALUES 
            (1, \x27merchant_zarrin_01\x27, \x27completed\x27, 15000000, 30000, CURRENT_TIMESTAMP),
            (2, \x27merchant_zarrin_01\x27, \x27completed\x27, 4500000, 9000, CURRENT_TIMESTAMP),
            (3, \x27merchant_zarrin_02\x27, \x27pending\x27, 8900000, 17800, CURRENT_TIMESTAMP),
            (4, \x27merchant_zarrin_02\x27, \x27failed\x27, 2000000, 4000, CURRENT_TIMESTAMP),
            (5, \x27merchant_zarrin_01\x27, \x27completed\x27, 35000000, 70000, CURRENT_TIMESTAMP);
        """)
    con.close()

def get_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    return duckdb.connect(DATABASE_PATH)
