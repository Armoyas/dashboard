"""ZarrinPal-specific business logic"""

from typing import Dict, List


def format_currency(amount: int) -> str:
    """Format amount in Iranian Rials with proper separators"""
    return f"{amount:,} ریال"


def get_session_status_name(status: str) -> str:
    """Get Persian name for session status"""
    status_map = {
        "SUCCESS": "موفق",
        "FAILED": "ناموفق",
        "EXPIRED": "منقضی شده",
        "REFUNDED": "برگشت داده شده"
    }
    return status_map.get(status, status)