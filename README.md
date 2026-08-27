# ZarrinPal Analytics Dashboard

Analytical dashboard for ZarrinPal payment data, built using Spec-Driven Development (SDD) methodology.

## Quick Start

```bash
git clone https://github.com/Armoyas/dashboard.git
cd dashboard
docker compose build --no-cache
docker compose up -d
```

Access the dashboard at: http://localhost:3000/

## Architecture

```
Client
  ↓
Nginx (port 80)
  ↓
Next.js (port 3000)   FastAPI (port 8000)
  ↓
DuckDB
  ← data/sample_data.csv  (input CSV)
```

- **Frontend**: Next.js 15.1.3 with standalone build
- **Backend**: FastAPI with uvicorn server
- **Database**: DuckDB for analytical queries
- **Data Source**: CSV input file (`data/sample_data.csv`) loaded into DuckDB on startup
- **Infrastructure**: Docker Compose, Nginx reverse proxy

## Data Source

The dashboard reads payment transaction data from a CSV file. By default it
expects the file at `data/sample_data.csv` (mounted into the container at
`/app/data/sample_data.csv`).

| Column | Description |
|--------|-------------|
| `session_key` | Unique session/transaction ID |
| `merchant_key` | Merchant identifier (e.g. `M1040`) |
| `amount` | Payment amount in Iranian Rials (IRR) |
| `adjusted_fee` | Fee indicator |
| `session_status` | Status: `Verified`, `Failed`, `InBank`, etc. |
| `created_at` | Timestamp of the payment attempt |

To use your own data, replace `data/sample_data.csv` with your ZarrinPal export
or mount a different CSV via the `DATA_FILE` environment variable:

```bash
DATA_FILE=/app/data/your_data.csv docker compose up -d --build
```

## Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Nginx | 80 | Reverse proxy, load balancer |
| Frontend | 3000 | Next.js application |
| Backend | 8000 | FastAPI API server |
| Adminer | 8080 | Database admin interface (optional) |

## API Endpoints

- `/api/health` - Health check
- `/api/merchants` - List all merchants
- `/api/analytics/overview` - Dashboard overview statistics
- `/api/analytics/merchant/{merchant_key}` - Merchant-specific analytics
- `/api/sessions` - List payment sessions
- `/api/sessions/{session_id}` - Get specific session details