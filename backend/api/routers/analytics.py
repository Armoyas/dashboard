"""
Analytics API router
Handles analytics and overview endpoints
"""

from fastapi import APIRouter, HTTPException
from api.database.connection import get_db_connection

router = APIRouter(tags=["analytics"])


@router.get("/analytics/overview")
async def get_overview():
    """
    Get analytics overview
    
    Returns high-level analytics data including total sessions,
    total amount, and success rates.
    """
    try:
        conn = get_db_connection()
        result = conn.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(CASE WHEN session_status = 'SUCCESS' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN session_status = 'FAILED' THEN 1 ELSE 0 END) as failed_count,
                COALESCE(SUM(amount), 0) as total_amount,
                COALESCE(SUM(adjusted_fee), 0) as total_fees
            FROM sessions
        """).fetchone()
        conn.close()
        
        return {
            "total_sessions": result[0],
            "success_count": result[1],
            "failed_count": result[2],
            "total_amount": result[3],
            "total_fees": result[4],
            "sessions": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/analytics/merchant/{merchant_key}")
async def get_merchant_analytics(merchant_key: str):
    """
    Get analytics for a specific merchant
    
    Returns detailed analytics for the merchant identified by merchant_key.
    """
    try:
        conn = get_db_connection()
        result = conn.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(CASE WHEN session_status = 'SUCCESS' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN session_status = 'FAILED' THEN 1 ELSE 0 END) as failed_count,
                COALESCE(SUM(amount), 0) as total_amount,
                COALESCE(SUM(adjusted_fee), 0) as total_fees
            FROM sessions
            WHERE merchant_key = ?
        """, [merchant_key]).fetchone()
        conn.close()
        
        if result[0] == 0:
            raise HTTPException(status_code=404, detail="Merchant not found")
        
        return {
            "merchant_key": merchant_key,
            "total_sessions": result[0],
            "success_count": result[1],
            "failed_count": result[2],
            "total_amount": result[3],
            "total_fees": result[4]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")