# pay/app/main.py

from fastapi import FastAPI, Request, Query, HTTPException, Header
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta, timezone
import asyncio
import httpx
import logging
import os
import re
import sqlite3
import time
import uuid as uuid_mod
import psycopg2

load_dotenv()
logging.basicConfig(level=logging.INFO)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

app = FastAPI(title="Smart98 Payment API")

MERCHANT_ID = os.getenv("ZARINPAL_MERCHANT_ID")
CALLBACK_URL = os.getenv("CALLBACK_URL", "https://smart98.ir/verify")
ZARINPAL_BASE = os.getenv("ZARINPAL_BASE_URL", "https://api.zarinpal.com/pg/v4")
ZARINPAL_WEB_BASE = os.getenv("ZARINPAL_WEB_BASE", "https://www.zarinpal.com/pg")

_raw_amount = os.getenv("STATIC_AMOUNT", "3000000")
try:
    STATIC_AMOUNT = int(_raw_amount)
except ValueError as exc:
    raise RuntimeError("STATIC_AMOUNT must be an integer") from exc

CASDOOR_ENDPOINT = (os.getenv("CASDOOR_ENDPOINT") or "https://auth.smart98.ir").rstrip("/")
CASDOOR_CLIENT_ID = (os.getenv("CASDOOR_CLIENT_ID") or "").strip()
CASDOOR_CLIENT_SECRET = (os.getenv("CASDOOR_CLIENT_SECRET") or "").strip()
CASDOOR_OWNER = (os.getenv("CASDOOR_OWNER") or "smart98").strip()

DB_FILE = os.getenv("PAY_DB_FILE", "/data/payments.db")
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "")
if not ADMIN_SECRET:
    logging.warning("ADMIN_SECRET is not set. Admin endpoints will be unprotected!")

logging.info("Using STATIC_AMOUNT=%s IRR", STATIC_AMOUNT)

origins = [
    "https://my.smart98.ir",
    "https://smart98.ir",
    "https://www.smart98.ir",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fixed regex — was missing closing bracket in original
_uuid_re = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

PAID_TYPE = "paid-user"
NORMAL_TYPE = "normal-user"

def _normalize_plan(value: Any) -> str:
    return PAID_TYPE if str(value or "").strip().lower() == PAID_TYPE else NORMAL_TYPE

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _parse_iso(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(value, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                continue
        return None

def _extract_casdoor_uuid(user_key: str) -> Optional[str]:
    """Extract Casdoor UUID from either a direct UUID string or an email pattern."""
    if not user_key:
        return None
    key = str(user_key).strip()
    if _uuid_re.match(key):
        return key
    match = re.match(r"casdoor-([0-9a-fA-F-]{36})@", key)
    if match:
        return match.group(1)
    return None

# --------------------------------------------------------------------------
# LobeChat database update – safe by full_name only
# --------------------------------------------------------------------------

def update_user_plan_in_lobechat(user_key: str, plan: str) -> bool:
    """Update the plan column in LobeChat's PostgreSQL users table."""
    db_url = os.getenv("LOBE_DATABASE_URL")
    if not db_url:
        logging.error("LOBE_DATABASE_URL not set")
        return False
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        # Match by id, full_name, or email LIKE for robust matching
        cur.execute(
            "UPDATE users SET plan = %s WHERE id = %s OR full_name = %s OR email LIKE %s",
            (plan, user_key, user_key, f"%{user_key}%")
        )
        conn.commit()
        cur.close()
        conn.close()
        logging.info("Updated LobeChat plan for user %s to %s", user_key, plan)
        return True
    except Exception as exc:
        logging.error("Failed to update LobeChat plan: %s", exc)
        return False

async def _request_json(
    method: str,
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
) -> Tuple[int, Any, str]:
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.request(method, url, params=params, json=json_body)
        raw = resp.text
        try:
            body = resp.json()
        except Exception:
            body = raw
        return resp.status_code, body, raw

async def _casdoor_get_user_variants(user_key: str) -> Optional[Dict[str, Any]]:
    if not CASDOOR_CLIENT_ID or not CASDOOR_CLIENT_SECRET:
        logging.error("Casdoor client credentials missing")
        return None
    key = str(user_key or "").strip()
    if not key:
        return None

    uuid_candidate = _extract_casdoor_uuid(key)
    variants = []

    if uuid_candidate:
        variants.append({
            "id": f"{CASDOOR_OWNER}/{uuid_candidate}",
            "clientId": CASDOOR_CLIENT_ID,
            "clientSecret": CASDOOR_CLIENT_SECRET,
        })
        variants.append({
            "userId": uuid_candidate,
            "clientId": CASDOOR_CLIENT_ID,
            "clientSecret": CASDOOR_CLIENT_SECRET,
        })
    else:
        variants.append({
            "id": f"{CASDOOR_OWNER}/{key}",
            "clientId": CASDOOR_CLIENT_ID,
            "clientSecret": CASDOOR_CLIENT_SECRET,
        })
        variants.append({
            "owner": CASDOOR_OWNER,
            "userId": key,
            "clientId": CASDOOR_CLIENT_ID,
            "clientSecret": CASDOOR_CLIENT_SECRET,
        })
        variants.append({
            "owner": CASDOOR_OWNER,
            "id": key,
            "clientId": CASDOOR_CLIENT_ID,
            "clientSecret": CASDOOR_CLIENT_SECRET,
        })
        variants.append({
            "owner": CASDOOR_OWNER,
            "name": key,
            "clientId": CASDOOR_CLIENT_ID,
            "clientSecret": CASDOOR_CLIENT_SECRET,
        })
        variants.append({
            "userId": key,
            "clientId": CASDOOR_CLIENT_ID,
            "clientSecret": CASDOOR_CLIENT_SECRET,
        })
        variants.append({
            "name": key,
            "clientId": CASDOOR_CLIENT_ID,
            "clientSecret": CASDOOR_CLIENT_SECRET,
        })

    for params in variants:
        try:
            status, body, _ = await _request_json(
                "GET",
                f"{CASDOOR_ENDPOINT}/api/get-user",
                params=params,
            )
        except Exception as exc:
            logging.error("Casdoor get-user failed: %s", exc)
            continue
        if status != 200:
            continue
        candidate = None
        if isinstance(body, dict):
            data = body.get("data")
            if isinstance(data, dict):
                candidate = data
            elif isinstance(data, list) and data:
                candidate = data[0]
            elif body.get("id") or body.get("name"):
                candidate = body
        elif isinstance(body, list) and body:
            candidate = body[0]
        if isinstance(candidate, dict):
            return candidate
    return None

async def _casdoor_update_user_type(user_key: str, user_type: str) -> bool:
    """Update the 'type' field on the Casdoor user object. This is a CACHED
    derivation — the source of truth is subscriptions. Called by the pay service
    after payment (upgrades) and by the expiry loop (downgrades)."""
    user_type = _normalize_plan(user_type)
    current = await _casdoor_get_user_variants(user_key)
    if not current:
        return False
    payload = dict(current)
    payload["owner"] = current.get("owner") or CASDOOR_OWNER
    payload["name"] = current.get("name") or str(user_key)
    payload["id"] = current.get("id") or str(user_key)
    payload["type"] = user_type
    payload["roles"] = (
        []
        if user_type == NORMAL_TYPE
        else [{"owner": CASDOOR_OWNER, "name": PAID_TYPE, "displayName": PAID_TYPE}]
    )
    payload["signupApplication"] = current.get("signupApplication") or "smart98-app"
    payload["displayName"] = current.get("displayName") or current.get("name") or str(user_key)
    payload["avatar"] = (
        current.get("avatar")
        or current.get("permanentAvatar")
        or "https://cdn.casbin.org/img/casbin.svg"
    )
    payload["email"] = current.get("email") or ""
    payload["phone"] = current.get("phone") or ""
    payload["isAdmin"] = bool(current.get("isAdmin", False))
    payload["isForbidden"] = bool(current.get("isForbidden", False))
    payload["isDeleted"] = bool(current.get("isDeleted", False))
    try:
        status, body, raw = await _request_json(
            "POST",
            f"{CASDOOR_ENDPOINT}/api/update-user",
            params={
                "id": f"{CASDOOR_OWNER}/{payload['name']}",
                "clientId": CASDOOR_CLIENT_ID,
                "clientSecret": CASDOOR_CLIENT_SECRET,
            },
            json_body=payload,
        )
    except Exception as exc:
        logging.error("Casdoor update-user failed: %s", exc)
        return False
    if status != 200:
        logging.error("Casdoor update-user returned %s: %s", status, raw)
        return False
    if isinstance(body, dict):
        return body.get("status") == "ok" or body.get("data") == "Affected"
    return True

# --------------------------------------------------------------------------
# Subscriptions – source of truth for paid/unpaid status
# --------------------------------------------------------------------------

async def _casdoor_get_subscriptions(user_param: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch all subscriptions for the CASDOOR_OWNER, then filter by user_param
    if provided. Handles both UUID and username lookups."""
    if not CASDOOR_CLIENT_ID or not CASDOOR_CLIENT_SECRET:
        return []
    params: Dict[str, Any] = {
        "owner": CASDOOR_OWNER,
        "clientId": CASDOOR_CLIENT_ID,
        "clientSecret": CASDOOR_CLIENT_SECRET,
    }
    try:
        status, body, _ = await _request_json(
            "GET",
            f"{CASDOOR_ENDPOINT}/api/get-subscriptions",
            params=params,
        )
    except Exception:
        return []
    if status != 200:
        return []
    subs = []
    if isinstance(body, dict):
        data = body.get("data")
        if isinstance(data, list):
            subs = data
        elif isinstance(data, dict):
            subs = [data]
    elif isinstance(body, list):
        subs = body

    if user_param:
        user_param_str = str(user_param)
        uuid_candidate = _extract_casdoor_uuid(user_param_str) or user_param_str

        subs = [
            s for s in subs
            if str(s.get("user") or s.get("userId") or "") == user_param_str
            or str(s.get("user") or s.get("userId") or "") == uuid_candidate
        ]
    return subs

def _is_active_subscription(sub: Dict[str, Any]) -> bool:
    """A subscription is active ONLY if:
    - state is exactly 'active' (not pending, upcoming, expired, suspended, etc.)
    - endTime is either absent or in the future
    """
    if not isinstance(sub, dict):
        return False
    state = str(sub.get("state") or sub.get("status") or "").strip().lower()
    if state != "active":
        return False
    end_raw = sub.get("endTime") or sub.get("end_time") or ""
    end_date = _parse_iso(end_raw)
    if end_date is None:
        return True  # no end date = perpetual
    return end_date >= _now_utc()

# --------------------------------------------------------------------------
# Subscription creation – always new, never overwrites
# --------------------------------------------------------------------------

async def _casdoor_create_subscription(user_key: str, months: int = 1) -> bool:
    """Always create a NEW subscription per successful payment.
    Never modify an existing subscription."""
    start_dt = _now_utc()
    end_dt = start_dt + timedelta(days=30 * months)
    sub_name = f"paid-sub-{user_key}-{uuid_mod.uuid4().hex[:12]}"
    payload = {
        "owner": CASDOOR_OWNER,
        "name": sub_name,
        "displayName": f"{user_key}-paid",
        "createdTime": start_dt.isoformat(),
        "description": f"Paid subscription for {user_key}",
        "user": user_key,
        "pricing": "",
        "plan": "paid-monthly",
        "payment": "Zarinpal",
        "startTime": start_dt.isoformat(),
        "endTime": end_dt.isoformat(),
        "period": "Monthly",
        "state": "Active",
    }
    status, body, raw = await _request_json(
        "POST",
        f"{CASDOOR_ENDPOINT}/api/add-subscription",
        params={
            "clientId": CASDOOR_CLIENT_ID,
            "clientSecret": CASDOOR_CLIENT_SECRET,
        },
        json_body=payload,
    )
    if status != 200:
        logging.error("Casdoor add-subscription failed (status %s): %s", status, raw)
        return False
    logging.info("Created subscription %s for user %s", sub_name, user_key)
    return True

async def _casdoor_downgrade_user(user_key: str) -> bool:
    """Downgrade the user to normal-user in both Casdoor (user.type cache)
    and LobeChat. The auth-validator will still check subscriptions first, so
    this is a secondary signal."""
    ok = await _casdoor_update_user_type(user_key, NORMAL_TYPE)
    update_user_plan_in_lobechat(user_key, NORMAL_TYPE)
    return ok

def _init_db() -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            authority TEXT PRIMARY KEY,
            user_id TEXT,
            username TEXT,
            created_at INTEGER,
            verified INTEGER DEFAULT 0,
            ref_id TEXT
        )
        """
    )
    conn.commit()
    cur.execute("PRAGMA table_info(payments)")
    cols = [r[1] for r in cur.fetchall()]
    if "username" not in cols:
        logging.info("Migrating payments table: adding username column")
        try:
            cur.execute("ALTER TABLE payments ADD COLUMN username TEXT")
            conn.commit()
        except Exception as exc:
            logging.error("Failed to add username column: %s", exc)
    conn.close()

_init_db()

def save_authority(authority: str, user_id: str, username: Optional[str] = None) -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO payments (authority, user_id, username, created_at, verified) VALUES (?, ?, ?, ?, 0)",
        (authority, user_id, username or "", int(time.time())),
    )
    conn.commit()
    conn.close()
    logging.info("Payment mapping saved")

def lookup_payment(authority: str) -> Tuple[Optional[str], str]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username FROM payments WHERE authority=?", (authority,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return (None, "")
    return (row[0], row[1] or "")

def mark_verified(authority: str, ref_id: str) -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE payments SET verified=1, ref_id=? WHERE authority=?", (ref_id, authority))
    conn.commit()
    conn.close()
    logging.info("Payment marked verified")

def already_verified(authority: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT verified FROM payments WHERE authority=?", (authority,))
    row = cur.fetchone()
    conn.close()
    return row is not None and row[0] == 1

# --------------------------------------------------------------------------
# Expiry loop – subscription state is the source of truth
# --------------------------------------------------------------------------

async def _run_one_expiry_iteration() -> None:
    """Check all subscriptions. If an 'active' subscription has endTime in the
    past, mark it as 'Expired'. Then downgrade the user ONLY if they have no
    other active subscription."""
    subs = await _casdoor_get_subscriptions()  # all subscriptions
    now = _now_utc()
    for s in subs:
        state = str(s.get("state") or s.get("status") or "").lower()
        end_time = s.get("endTime") or s.get("end_time") or ""
        sub_name = s.get("name") or ""
        user_key = s.get("user") or s.get("userId") or ""

        if not sub_name or not user_key or not end_time:
            continue

        parsed = _parse_iso(end_time)
        if parsed is None:
            continue

        # Expire if active and past its end time
        if state == "active" and parsed < now:
            payload = dict(s)
            payload["owner"] = CASDOOR_OWNER
            payload["name"] = sub_name
            payload["user"] = user_key
            payload["state"] = "Expired"

            try:
                status, body, raw = await _request_json(
                    "POST",
                    f"{CASDOOR_ENDPOINT}/api/update-subscription",
                    params={
                        "id": f"{CASDOOR_OWNER}/{sub_name}",
                        "clientId": CASDOOR_CLIENT_ID,
                        "clientSecret": CASDOOR_CLIENT_SECRET,
                    },
                    json_body=payload,
                )
                if status == 200:
                    logging.info(
                        "Subscription %s expired for user %s",
                        sub_name, user_key
                    )
                    # Check if user still has ANY other active subscription
                    user_subs = await _casdoor_get_subscriptions(user_key)
                    has_active = any(_is_active_subscription(s) for s in user_subs)
                    if not has_active:
                        logging.info(
                            "No active subscriptions left for %s, downgrading to normal-user",
                            user_key
                        )
                        await _casdoor_downgrade_user(user_key)
                    else:
                        logging.info(
                            "User %s still has another active subscription, skipping downgrade",
                            user_key
                        )
                else:
                    logging.error(
                        "Failed to mark subscription %s as expired (status %s): %s",
                        sub_name, status, raw
                    )
            except Exception as exc:
                logging.error("Failed to expire subscription %s: %s", sub_name, exc)

async def _expiry_loop(interval_seconds: int) -> None:
    logging.info("Starting subscription expiry checker (interval %ds)", interval_seconds)
    while True:
        try:
            await _run_one_expiry_iteration()
        except Exception as exc:
            logging.error("Subscription expiry loop failed: %s", exc)
        await asyncio.sleep(interval_seconds)

@app.on_event("startup")
async def start_background_tasks() -> None:
    interval_seconds = int(os.getenv("SUBSCRIPTION_CHECK_INTERVAL", "3600"))
    asyncio.create_task(_expiry_loop(interval_seconds))

def _check_admin_secret(header_secret: Optional[str]) -> bool:
    if not ADMIN_SECRET:
        return True
    if not header_secret:
        return False
    return header_secret == ADMIN_SECRET

@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/pay")
async def create_payment(request: Request):
    if not MERCHANT_ID:
        raise HTTPException(status_code=500, detail="ZARINPAL_MERCHANT_ID is not set")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")
    user_id = data.get("userId")
    username = data.get("username")
    if not user_id:
        raise HTTPException(status_code=400, detail="userId is required")
    description = data.get("description", "Upgrade to paid-user")
    payload = {
        "merchant_id": MERCHANT_ID,
        "amount": STATIC_AMOUNT,
        "currency": "IRR",
        "description": description,
        "callback_url": CALLBACK_URL,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{ZARINPAL_BASE}/payment/request.json", json=payload)
        try:
            body = resp.json()
        except Exception:
            raise HTTPException(status_code=502, detail="invalid zarinpal response")
    if body.get("data", {}).get("code") == 100:
        authority = body["data"]["authority"]
        start_url = f"{ZARINPAL_WEB_BASE}/StartPay/{authority}"
        save_authority(authority, str(user_id), username)
        return JSONResponse({"url": start_url})
    return JSONResponse({"error": body.get("errors", {})}, status_code=400)

@app.get("/verify")
async def verify_payment(authority: str = Query(None, alias="Authority"), status: str = Query(None, alias="Status")):
    if not MERCHANT_ID:
        raise HTTPException(status_code=500, detail="ZARINPAL_MERCHANT_ID is not set")
    if not authority:
        return RedirectResponse("https://my.smart98.ir/payment-failed")
    if status != "OK":
        return RedirectResponse("https://my.smart98.ir/payment-canceled")
    if already_verified(authority):
        logging.info("Payment already verified, redirecting to success")
        return RedirectResponse(
            "https://my.smart98.ir/?upgrade=already-completed&forceRefresh=1"
        )
    payload = {"merchant_id": MERCHANT_ID, "amount": STATIC_AMOUNT, "authority": authority}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{ZARINPAL_BASE}/payment/verify.json", json=payload)
        try:
            body = resp.json()
        except Exception:
            return RedirectResponse("https://my.smart98.ir/payment-failed")
    code = body.get("data", {}).get("code")
    if code in [100, 101]:
        ref_id = str(body["data"].get("ref_id", ""))
        mark_verified(authority, ref_id)
        user_id, username = lookup_payment(authority)
        if not user_id and not username:
            return RedirectResponse("https://my.smart98.ir/payment-failed")
        lookup_key = username or user_id or ""
        casdoor_user = await _casdoor_get_user_variants(lookup_key)
        if not casdoor_user:
            casdoor_user = await _casdoor_get_user_variants(str(user_id or ""))
        if not casdoor_user:
            return RedirectResponse("https://my.smart98.ir/payment-failed")
        user_key = str(casdoor_user.get("name") or casdoor_user.get("id") or lookup_key).strip()
        if not user_key:
            return RedirectResponse("https://my.smart98.ir/payment-failed")
        try:
            await _casdoor_update_user_type(user_key, PAID_TYPE)
        except Exception as exc:
            logging.warning("User type update after payment failed: %s", exc)
        update_user_plan_in_lobechat(user_key, PAID_TYPE)
        try:
            await _casdoor_create_subscription(user_key, months=1)
        except Exception as exc:
            logging.warning("Subscription creation after payment failed: %s", exc)
        return RedirectResponse(
            f"https://my.smart98.ir/?upgrade=success&user={user_key}&forceRefresh=1#upgrade-success"
        )
    return RedirectResponse("https://my.smart98.ir/payment-failed")

@app.get("/admin/subscriptions")
async def admin_list_subscriptions(user: Optional[str] = None, x_admin_secret: Optional[str] = Header(None)):
    if not _check_admin_secret(x_admin_secret):
        raise HTTPException(status_code=403, detail="forbidden")
    subs = await _casdoor_get_subscriptions(user)
    return JSONResponse({"count": len(subs), "data": subs})

@app.post("/admin/downgrade")
async def admin_downgrade_user(username: str = Query(...), x_admin_secret: Optional[str] = Header(None)):
    if not _check_admin_secret(x_admin_secret):
        raise HTTPException(status_code=403, detail="forbidden")
    ok = await _casdoor_downgrade_user(username)
    return JSONResponse({"username": username, "downgraded": ok})

@app.post("/admin/run-expiry")
async def admin_run_expiry(x_admin_secret: Optional[str] = Header(None)):
    if not _check_admin_secret(x_admin_secret):
        raise HTTPException(status_code=403, detail="forbidden")
    try:
        await _run_one_expiry_iteration()
        return JSONResponse({"ran": True})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
