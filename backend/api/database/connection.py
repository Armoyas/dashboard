"""Database connection management for DuckDB"""

import duckdb
from typing import Optional
import os

# Default database path
DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/analytics.duckdb")


def get_connection() -> duckdb.DuckDBPyConnection:
    """Get a DuckDB database connection"""
    return duckdb.connect(DATABASE_PATH)


def get_db_connection():
    """Get a database connection (compatible with dependency injection)"""
    conn = get_connection()
    return conn