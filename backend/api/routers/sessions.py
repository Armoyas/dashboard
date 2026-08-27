"""
Sessions API router
Handles payment session endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from api.database.connection import get_db_connection

router = APIRouter(tags=["sessions"])


@router.get("/sessions")
async def list_sessions(limit: int = 100, offset: int = 0):
    """
    List payment sessions

    Returns a paginated list of payment sessions with optional filtering.
    """
    try:
        conn = get_db_connection()
        sessions = conn.execute("""
            SELECT id, merchant_key, session_status, amount, adjusted_fee, created_at
            FROM sessions
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, [limit, offset]).fetchall()

        return {
            "sessions": [
                {
                    "id": s[0],
                    "merchant_key": s[1],
                    "session_status": s[2],
                    "amount": s[3],
                    "adjusted_fee": s[4],
                    "created_at": s[5].isoformat() if s[5] else None
                }
                for s in sessions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get a specific session by ID

    Returns detailed information about a specific payment session.
    """
    try:
        conn = get_db_connection()
        session = conn.execute("""
            SELECT id, merchant_key, session_status, amount, adjusted_fee,
                   authority, email, mobile, created_at, updated_at
            FROM sessions
            WHERE id = ?
        """, [session_id]).fetchone()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "id": session[0],
            "merchant_key": session[1],
            "session_status": session[2],
            "amount": session[3],
            "adjusted_fee": session[4],
            "authority": session[5],
            "email": session[6],
            "mobile": session[7],
            "created_at": session[8].isoformat() if session[8] else None,
            "updated_at": session[9].isoformat() if session[9] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
