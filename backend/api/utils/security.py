"""Security and validation utilities"""

import re


def sanitize_merchant_key(merchant_key: str) -> str:
    """Sanitize merchant key to prevent injection"""
    return re.sub(r'[^a-zA-Z0-9_-]', '', merchant_key)