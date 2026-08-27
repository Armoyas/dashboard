"""Pydantic data schemas for API request/response validation"""

from pydantic import BaseModel
from typing import List, Optional


class MerchantBase(BaseModel):
    merchant_key: str
    name: str


class MerchantResponse(BaseModel):
    merchants: List[MerchantBase]


class SessionBase(BaseModel):
    id: str
    merchant_key: str
    session_status: str
    amount: int
    adjusted_fee: int


class SessionResponse(BaseModel):
    sessions: List[SessionBase]