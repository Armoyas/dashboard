"""Database connection management for DuckDB.

Data is loaded from an input CSV file (default: data/sample_data.csv) rather
than hardcoded sample rows. This aligns the dashboard with the reference
analytical-dashboard repo's CSV-driven data ingestion approach.
"""
import duckdb
import os
from typing import Optional
from pathlib import Path

# --- Configuration --------------------------------------------------------

# Path to the DuckDB database file
DATABASE_PATH = os.getenv("DATABASE_PATH")
if not DATABASE_PATH:
    docker_path = "/app/database/analytics.duckdb"
    local_path = str(Path(__file__).resolve().parents[4] / "backend/database/analytics.duckdb")
    DATABASE_PATH = docker_path if Path("/app").exists() else local_path

# Path to the SQL schema file
SCHEMA_PATH = os.getenv("SCHEMA_PATH")
if not SCHEMA_PATH:
    docker_path = "/app/database/schema.sql"
    local_path = str(Path(__file__).resolve().parents[4] / "database/schema.sql")
    SCHEMA_PATH = docker_path if Path("/app").exists() else local_path

# Path to the input CSV data file.
# In Docker the CSV is mounted at /app/data/sample_data.csv (see docker-compose).
DATA_FILE = os.getenv("DATA_FILE")
if not DATA_FILE:
    docker_path = "/app/data/sample_data.csv"
    local_path = str(Path(__file__).resolve().parents[4] / "data/sample_data.csv")
    DATA_FILE = docker_path if Path("/app").exists() else local_path

_connection: Optional[duckdb.DuckDBPyConnection] = None


# --- Connection management -------------------------------------------------

def get_connection() -> duckdb.DuckDBPyConnection:
    """Get or create the singleton DuckDB connection."""
    global _connection
    if _connection is None:
        Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
        _connection = duckdb.connect(database=DATABASE_PATH, read_only=False)
        _init_schema()
        _load_csv_data()
    return _connection


def _init_schema() -> None:
    """Apply the SQL schema script if the database is empty."""
    if _connection is None:
        return
    # Check if tables already exist
    tables = _connection.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main'"
    ).fetchall()
    if tables:
        return  # schema already applied
    schema_file = Path(SCHEMA_PATH)
    if schema_file.exists():
        _connection.execute(schema_file.read_text())
        _connection.commit()


def _load_csv_data() -> None:
    """Load data from the input CSV file into the merchants/sessions/transactions tables.

    The CSV is expected to have columns matching the ZarrinPal transaction schema
    (session_key, merchant_key, amount, adjusted_fee, session_status, etc.).

    This replaces the previous hardcoded _insert_sample_data() approach so the
    dashboard is driven entirely by the input data file.
    """
    if _connection is None:
        return

    csv_path = Path(DATA_FILE)
    if not csv_path.exists():
        # Fall back to a small built-in sample so the app still runs without a CSV.
        _insert_fallback_sample()
        return

    # Load CSV into a temporary staging table, then redistribute into the
    # normalized merchants / sessions / transactions tables.
    _connection.execute(f"""
        CREATE OR REPLACE TABLE _csv_staging AS
        SELECT * FROM read_csv_auto('{csv_path}', header=true, sep=',')
    """)

    # Populate merchants table (deduplicated by merchant_key)
    _connection.execute("""
        INSERT INTO merchants (merchant_key, name)
        SELECT DISTINCT merchant_key,
               COALESCE(MIN(NULLIF(category_title, '')), 'Unknown Merchant')
        FROM _csv_staging
        GROUP BY merchant_key
        ON CONFLICT (merchant_key) DO NOTHING
    """)

    # Populate sessions table from CSV data
    # CSV columns: session_key, try_seq, terminal_key, merchant_key,
    # category_id, category_title, amount, adjusted_fee, session_status,
    # try_status, switch_response_code, psp_code, issuer_bank_code,
    # payer_card_key, verify_type, init_time_ms, verify_time_ms,
    # created_at, try_created_at, verified_at, settled_at, expire_in
    _connection.execute("""
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
            NULL,  -- email
            NULL,  -- mobile
            created_at::TIMESTAMP,
            COALESCE(verified_at::TIMESTAMP, created_at::TIMESTAMP)
        FROM _csv_staging
        ON CONFLICT (id) DO NOTHING
    """)

    # Clean up staging table
    _connection.execute("DROP TABLE _csv_staging")
    _connection.commit()


def _insert_fallback_sample() -> None:
    """Insert minimal fallback data when no CSV file is available."""
    _connection.execute("""
        INSERT INTO merchants (merchant_key, name) VALUES
            ('test_merchant_001', 'Test Merchant One'),
            ('test_merchant_002', 'Test Merchant Two')
        ON CONFLICT (merchant_key) DO NOTHING
    """)
    sample_sessions = [
        ('550e8400-e29b-41d4-a716-446655440000', 'test_merchant_001', 'SUCCESS', 500000, 15000, 'auth123', None, None),
        ('6ba7b810-9dad-11d1-80b4-00c04fd430c8', 'test_merchant_002', 'FAILED', 300000, 9000, 'auth456', None, None),
        ('f47ac10b-58cc-4372-a567-0e02b2c3d479', 'test_merchant_001', 'SUCCESS', 750000, 22500, 'auth789', None, None),
    ]
    for session in sample_sessions:
        _connection.execute(
            "INSERT INTO sessions (id, merchant_key, session_status, amount, adjusted_fee, authority, email, mobile) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (id) DO NOTHING",
            session
        )
    _connection.commit()


def get_db_connection():
    """Get a database connection (dependency injection compatible).
    Returns the singleton connection - do NOT close it in routes.
    """
    return get_connection()


def close_connection():
    """Close the database connection (called on shutdown)."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
