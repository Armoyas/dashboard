# PROJECT_HANDOFF.md

## Project: dashboard
An SDD-methodology analytical dashboard for ZarrinPal payment data, built on the Armoyas/analytical-dashboard reference.

## Project Structure

```
dashboard/
├── docker-compose.yml     # Docker Compose configuration
├── nginx/
│   └── nginx.conf         # Nginx reverse proxy configuration
├── frontend/              # Next.js 15.1.3 application
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── styles/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── dashboard/page.tsx
│   └── components/
│       ├── MerchantSelector.tsx
│       ├── AnalyticsChart.tsx
│       └── DataTable.tsx
├── backend/               # FastAPI API service
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── api/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── merchants.py
│   │   │   ├── analytics.py
│   │   │   └── sessions.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── queries.py
│   │   └── services/
│   │       └── zarrinpal.py
│   └── utils/
│       ├── security.py
│       └── helpers.py
├── database/
│   └── schema.sql         # DuckDB schema initialization
└── specs/
    └── stage1/            # Stage 1 specifications
        ├── components.md
        ├── api-specs.md
        ├── database.md
        ├── deployment.md
        ├── testing.md
        └── validation.md
```

## Quick Start

```bash
# Clone
git clone https://github.com/Armoyas/dashboard.git
cd dashboard

# Deploy
docker compose build --no-cache
docker compose up -d
```

## Architecture Summary
```
Client → Nginx (80) → Next.js (3000) or FastAPI (8000) → DuckDB
```

## Key Specifications
- **Frontend**: Next.js 15.1.3 (standalone build)
- **Backend**: FastAPI with uvicorn server on port 8000
- **Database**: DuckDB with ZarrinPal schema (merchants, sessions, transactions)
- **Infra**: Docker Compose, Nginx reverse proxy
- **Known Issues Addressed**:
  - Null-safety pattern: `(merchants || []).find()`
  - `force-dynamic` rendering for dashboard pages
  - `--no-cache` builds required for Next.js 14→15 fixes

## ZarrinPal Schema
- merchant_key (PK for merchants)
- session_status (SUCCESS, FAILED, EXPIRED, REFUNDED)
- amount (in Rials/Iranian IRR)
- adjusted_fee (processing fee)
- No customer_id or product_id fields

## Validation Results
All Stage 1 scaffold files verified with 83 syntax checks passed.

## Next Steps
- **Stage 2**: Implement advanced features (charts, filtering, exports)
- **Stage 3**: Production deployment to 62.60.198.209
- **Stage 4**: Testing and optimization