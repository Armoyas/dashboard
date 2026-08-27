# Stage 1: Component Specifications

## System Components

### Overview
The dashboard system follows a three-tier architecture:
```
Client → Nginx (Reverse Proxy) → Next.js Frontend OR FastAPI Backend → DuckDB
```

Components:
1. **Frontend Layer**: Next.js 15.1.3 application
2. **Backend Layer**: FastAPI service
3. **Data Layer**: DuckDB database
4. **Infrastructure Layer**: Nginx, Docker Compose, uvicorn

---

## Frontend Component (Next.js 15.1.3)

### Structure
```
frontend/
├── Dockerfile
├── package.json
├── next.config.js
├── tailwind.config.js
├── styles/
│   └── globals.css
├── app/
│   ├── layout.tsx     # Root layout (RTL, Persian)
│   ├── page.tsx       # Landing page
│   └── dashboard/
│       └── page.tsx   # Main dashboard view
├── components/
│   ├── MerchantSelector.tsx
│   ├── AnalyticsChart.tsx
│   └── DataTable.tsx
└── public/
    └── fonts/
        └── Vazirmatn.woff2
```

### Configuration
- `next.config.js`:
  - `output: 'standalone'` for Docker deployment
  - `reactStrictMode: true`
  - `trailingSlash: false` (default)
  - `swcMinify: true`
  - API rewrites to backend

### Dependencies
- React 19 (via Next.js 15)
- TypeScript
- TailwindCSS v3.4 for styling
- Recharts for visualizations
- clsx for conditional classnames
- dayjs for date formatting
- @headlessui/react for UI components

### Known Constraints
- Use `force-dynamic` in page rendering to prevent prerendering issues
- Apply null-safety patterns: `(merchants || []).find(m => m.id === selectedId)`
- Handle RTL (Persian) support with `dir="rtl"` on html element
- Use Vazirmatn font via TailwindCSS configuration

---

## Backend Component (FastAPI)

### Structure
```
backend/
├── Dockerfile
├── requirements.txt
├── api/
│   ├── main.py             # FastAPI app entry point
│   ├── routers/
│   │   ├── merchants.py    # Merchant-related endpoints
│   │   ├── analytics.py    # Analytics/data endpoints
│   │   └── sessions.py     # Payment session endpoints
│   ├── models/
│   │   └── schemas.py      # Pydantic models
│   ├── database/
│   │   ├── connection.py   # DuckDB connection management
│   │   └── queries.py      # Pre-defined SQL queries
│   ├── services/
│   │   └── zarrinpal.py    # ZarrinPal-specific logic
│   └── utils/
│       ├── security.py     # Auth/validation
│       └── helpers.py      # Utility functions
```

### Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/merchants` | List all merchants |
| GET | `/api/analytics/overview` | Dashboard overview stats |
| GET | `/api/analytics/merchant/{merchant_key}` | Per-merchant analytics |
| GET | `/api/sessions` | List payment sessions |
| GET | `/api/sessions/{session_id}` | Get specific session |

### Dependencies
- FastAPI 0.115.0
- uvicorn 0.30.6 (ASGI server)
- DuckDB 1.1.0 (analytical database)
- Pydantic 2.9.2 (data validation)
- SQLAlchemy 2.0.35 (ORM)
- pydantic-settings 2.5.2

### Configuration
- Run with: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
- Database path: `/app/data/analytics.duckdb`
- CORS middleware enabled for all origins

---

## Data Layer (DuckDB)

### Schema
#### merchants Table
```sql
CREATE TABLE merchants (
    merchant_key VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### sessions Table (ZarrinPal Core)
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    merchant_key VARCHAR REFERENCES merchants(merchant_key),
    session_status VARCHAR NOT NULL,
    amount BIGINT, -- In Rials (IRR)
    adjusted_fee BIGINT, -- Processing fee
    authority VARCHAR,
    email VARCHAR,
    mobile VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### transactions Table
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    status VARCHAR,
    amount BIGINT,
    fee BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
```sql
CREATE INDEX idx_sessions_merchant_key ON sessions(merchant_key);
CREATE INDEX idx_sessions_status ON sessions(session_status);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
```

---

## Infrastructure Layer

### Docker Compose Configuration
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://backend:8000/api
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_PATH=/app/data/analytics.duckdb
    restart: unless-stopped
```

### Nginx Configuration
```nginx
events { }

http {
    upstream frontend { server frontend:3000; }
    upstream backend { server backend:8000; }
    
    server {
        listen 80;
        
        location / {
            proxy_pass http://frontend;
        }
        
        location /api/ {
            proxy_pass http://backend;
        }
    }
}
```

### Server Information (Reference)
- Host: 62.60.198.209
- Nginx Port: 80 (Public)
- Next.js Port: 3000 (Internal)
- FastAPI Port: 8000 (Internal)
- SSH Access: Not available (port 22 filtered)
- Deployment User: root (password: LgimS@^c8i)