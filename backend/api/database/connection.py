"""Database connection management for DuckDB"""
import duckdb
from typing import Optional, Generator
import os
from pathlib import Path

# Default database paths - works in Docker and locally
DATABASE_PATH = os.getenv("DATABASE_PATH")
if not DATABASE_PATH:
    # Try Docker path first, fall back to local project path
    docker_path = "/app/database/analytics.duckdb"
    local_path = str(Path(__file__).resolve().parents[3] / "database/analytics.duckdb")
    DATABASE_PATH = docker_path if Path(docker_path).parent.exists() else local_path

SCHEMA_PATH = os.getenv("SCHEMA_PATH")
if not SCHEMA_PATH:
    docker_path = "/app/database/schema.sql"
    local_path = str(Path(__file__).resolve().parents[3] / "database/schema.sql")
    SCHEMA_PATH = docker_path if Path(docker_path).exists() else local_path

_connection: Optional[duckdb.DuckDBPyConnection] = None


def get_connection() -> duckdb.DuckDBPyConnection:
    """Get or create the singleton DuckDB connection."""
    global _connection
    if _connection is None:
        Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
        _connection = duckdb.connect(database=DATABASE_PATH, read_only=False)
        _init_schema()
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
        # Insert sample data
        _insert_sample_data()


def _insert_sample_data() -> None:
    """Insert sample data for testing and demonstration."""
    _connection.execute("""
        INSERT INTO merchants (merchant_key, name) VALUES
            ('test_merchant_001', 'Test Merchant One'),
            ('test_merchant_002', 'Test Merchant Two')
        ON CONFLICT (merchant_key) DO NOTHING;
    """)
    # DuckDB accepts UUID strings directly in INSERT statements
    # Use individual INSERTs for each session to avoid multi-row issues
    sample_sessions = [
        ('550e8400-e29b-41d4-a716-446655440000', 'test_merchant_001', 'SUCCESS', 500000, 15000, 'auth123', 'user1@test.com', '09120000001'),
        ('6ba7b810-9dad-11d1-80b4-00c04fd430c8', 'test_merchant_002', 'FAILED', 300000, 9000, 'auth456', 'user2@test.com', '09120000002'),
        ('f47ac10b-58cc-4372-a567-0e02b2c3d479', 'test_merchant_001', 'SUCCESS', 750000, 22500, 'auth789', 'user3@test.com', '09120000003'),
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
