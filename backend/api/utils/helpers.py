"""Helper functions"""

from datetime import datetime


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string with timezone"""
    if dt:
        return dt.isoformat() + "Z"
    return None