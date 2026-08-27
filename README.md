# Dashboard - ZarrinPal Analytics

An analytical dashboard for ZarrinPal payment data, built using Spec-Driven Development (SDD) methodology.

## Quick Start

```bash
git clone https://github.com/Armoyas/dashboard.git
cd dashboard
docker compose build --no-cache
docker compose up -d
```

Access the dashboard at: http://62.60.198.209/

## Architecture

```
Client
  ↓
Nginx (port 80)
  ↓
Next.js (port 3000)   FastAPI (port 8000)
  ↓
DuckDB
```

- **Frontend**: Next.js 15.1.3 with standalone build
- **Backend**: FastAPI + uvicorn
- **Database**: DuckDB
- **Infra**: Docker Compose + Nginx

## Data Schema

| Table | Columns |
|-------|---------|
| merchants | merchant_key (PK), name, created_at |
| sessions | id (PK), merchant_key, session_status, amount (Rials), adjusted_fee |
| transactions | id (PK), session_id, status, amount, fee |

## Specifications

This project follows SDD methodology with specifications in `/specs/`:

- **Stage 0**: High-level requirements and architecture
- **Stage 1**: Detailed component specs and API contracts

See [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) for full details.

## Testing

```bash
# Backend
cd api && pytest tests/

# Frontend
cd next-app && npm test
```

## License

MIT
