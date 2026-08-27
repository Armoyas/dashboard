"""
Merchants API router
Handles merchant-related endpoints
"""

from fastapi import APIRouter, HTTPException
from api.models.schemas import MerchantResponse
from api.database.connection import get_db_connection

router = APIRouter(tags=["merchants"])


@router.get("/merchants", response_model=MerchantResponse)
async def list_merchants():
    """
    List all merchants
    
    Returns a list of all merchants registered in the system.
    """
    try:
        conn = get_db_connection()
        merchants = conn.execute("SELECT * FROM merchants ORDER BY name").fetchall()
        conn.close()
        
        return MerchantResponse(
            merchants=[
                {"merchant_key": m[0], "name": m[1]}
                for m in merchants
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")