# Architecture

> Reference Repository: Armoyas/analytical-dashboard
> New Repository: Armoyas/dashboard
> Stage: Stage 0

## 1. Overview

This document describes the high-level architecture of the dashboard application, based on the reference architecture from Armoyas/analytical-dashboard.

## 2. Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                            │
└──────────────────────┬─────────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │    Nginx        │ Port 80
              │ Reverse Proxy   │
              └────────┬────────┘
             ┌─────────┴──────────┐
             │                    │
      ┌──────▼──────┐      ┌─────▼──────┐
      │  Frontend   │      │  API       │
      │ Next.js     │      │ FastAPI    │
      │ Port 3000   │      │ Port 8000  │
      └──────┬──────┘      └─────┬──────┘
             │                    │
             │              ┌─────▼──────┐
             │              │  DuckDB    │
             │              │ Analytics  │
             │              │ Database   │
             └──────────────┴────────────┘
                            (Data Store)
```

## 3. Component Specifications

### 3.1 Nginx (Reverse Proxy)

| Attribute | Value |
|-----------|-------|
| **Version** | 1.31.4+ |
| **Port** | 80 (external) |
| **Responsibilities** | - Route `/api/*` to FastAPI backend<br>- Route `/*` to Next.js frontend<br>- Serve static assets |
| **Configuration** | `/app/nginx/nginx.conf` |

### 3.2 Frontend (Next.js)

| Attribute | Value |
|-----------|-------|
| **Version** | Next.js 15.1.3+ |
| **Port** | 3000 (internal) |
| **Output** | Standalone build output |
| **Responsibilities** | - Dashboard UI rendering<br>- Server-side data fetching<br>- Merchant filtering |
| **Key Fix** | `force-dynamic` in next.config.js to avoid prerendering errors<br>`(merchants || []).find()` null-safety pattern |

### 3.3 API (FastAPI)

| Attribute | Value |
|-----------|-------|
| **Version** | Latest stable |
| **Port** | 8000 (internal) |
| **Framework** | FastAPI + uvicorn |
| **Responsibilities** | - Transaction data queries<br>- Merchant-specific analytics<br>- JSON API responses |

### 3.4 Database (DuckDB)

| Attribute | Value |
|-----------|-------|
| **Version** | Latest stable |
| **Storage** | Persistent volume |
| **Schema** | ZarrinPal analytics schema |
| **Fields** | `merchant_key` (string), `session_status` (string), `amount` (integer, IRR), `adjusted_fee` (integer) |

## 4. Data Flow

1. **Client Request**: User accesses dashboard via browser → Nginx (port 80)
2. **Routing**: Nginx routes based on path:
   - `/api/*` → FastAPI backend
   - `/*` → Next.js frontend
3. **API Processing**: FastAPI queries DuckDB for analytics data
4. **Data Response**: API returns JSON to frontend or directly to client
5. **Frontend Rendering**: Next.js renders dashboard UI with data

## 5. Deployment Architecture

```
┌───────────────────────────────────────────────┐
│              Host: 62.60.198.209             │
│                                              │
│  ┌──────────────┐ ┌──────────────┐           │
│  │    Nginx     │ │ Docker Host  │           │
│  │  Port 80     │ │              │           │
│  └──────┬───────┘ └──────┬───────┘           │
│         │              │                   │
│  ┌──────▼──────┐  ┌────▼────┐ ┌──────────┐ │
│  │   Nginx     │  │Frontend │ │   API    │ │
│  │ Container   │  │Container│ │Container │ │
│  │             │  │ Next.js │ │ FastAPI  │ │
│  │             │  │ Port 3K │ │ Port 8K  │ │
│  └──────┬──────┘  └────┬────┘ └──────────┘ │
│         │              │                   │
│         │         ┌────▼────┐             │
│         │         │ DuckDB │             │
│         │         │ Volume │             │
│         │         └────────┘             │
│         └─────────────────────────────────┘
└───────────────────────────────────────────────┘
```

## 6. Reference Implementation Notes

From Armoyas/analytical-dashboard:

1. **Docker Compose structure**:
   - `api` service: FastAPI + uvicorn, port 8000
   - `frontend` service: Next.js 15.1.3 standalone, port 3000
   - `nginx` service: Reverse proxy, port 80

2. **Build configuration**:
   - `next.config.js`: `output: 'standalone'` + `force-dynamic`
   - `docker-compose.yml`: `cache: false` (standalone doesn't support)
   - Build command: `docker compose build --no-cache`

3. **Null safety pattern**:
   - Component files use `(merchants || []).find(...)` pattern
   - Applied to all array operations

4. **SSH deployment**:
   - Direct SSH blocked (port 22 filtered)
   - Deployment via curl script or git remote URL extraction
