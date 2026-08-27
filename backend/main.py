from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import connection

app = FastAPI(title="ZarrinPal Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    connection.init_db()

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/transactions")
def get_transactions(
    merchant_key: Optional[str] = None,
    session_status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    con = connection.get_connection()
    query = "SELECT id, merchant_key, session_status, amount, adjusted_fee, strftime(created_at, \x27%Y-%m-%dT%H:%M:%SZ\x27) as created_at FROM transactions WHERE 1=1"
    params = []
    
    if merchant_key:
        query += " AND merchant_key = ?"
        params.append(merchant_key)
    if session_status:
        query += " AND session_status = ?"
        params.append(session_status)
        
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    rows = con.execute(query, params).fetchall()
    total = con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    con.close()
    
    transactions = [
        {
            "id": r[0],
            "merchant_key": r[1],
            "session_status": r[2],
            "amount": r[3],
            "adjusted_fee": r[4],
            "created_at": r[5],
        }
        for r in rows
    ]
    return {"transactions": transactions, "count": len(transactions), "total": total}

@app.get("/api/merchants")
def get_merchants():
    con = connection.get_connection()
    rows = con.execute("SELECT merchant_key, name, strftime(created_at, \x27%Y-%m-%dT%H:%M:%SZ\x27) FROM merchants").fetchall()
    con.close()
    return [{"merchant_key": r[0], "name": r[1], "created_at": r[2]} for r in rows]

@app.get("/api/stats/summary")
def get_summary_stats():
    con = connection.get_connection()
    tx_count = con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    total_volume = con.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE session_status=\x27completed\x27").fetchone()[0]
    total_fees = con.execute("SELECT COALESCE(SUM(adjusted_fee), 0) FROM transactions WHERE session_status=\x27completed\x27").fetchone()[0]
    merchants_count = con.execute("SELECT COUNT(DISTINCT merchant_key) FROM merchants").fetchone()[0]
    con.close()
    
    return {
        "total_transactions": tx_count,
        "total_volume": total_volume,
        "total_fees": total_fees,
        "active_merchants": merchants_count
    }
