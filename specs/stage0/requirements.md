# Requirements

> Reference Repository: Armoyas/analytical-dashboard
> New Repository: Armoyas/dashboard
> Stage: Stage 0

## 1. Problem Statement

A dashboard application needs to be built using the Spec-Driven Development methodology. The application should visualize ZarrinPal payment analytics data, building upon the architectural patterns established in the reference repository Armoyas/analytical-dashboard.

## 2. Functional Requirements

### 2.1 Dashboard Overview

| ID | Requirement | Priority |
|----|------------|----------|
| FR-01 | Display summary statistics of ZarrinPal payment transactions | High |
| FR-02 | Show transaction data with filters by merchant, status, and date | High |
| FR-03 | Provide API endpoints for all dashboard data | High |
| FR-04 | Serve React frontend via Next.js with server-side rendering | Medium |

### 2.2 API Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| FR-05 | RESTful API built with FastAPI | High |
| FR-06 | Support transaction data retrieval | High |
| FR-07 | Support merchant-specific data queries | High |
| FR-08 | Return data in JSON format | High |

### 2.3 Data Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| FR-09 | Store ZarrinPal analytics data in DuckDB | High |
| FR-10 | Maintain merchant_key, session_status, amount, adjusted_fee fields | High |
| FR-11 | Amount stored in Iranian Rials (IRR) | High |

## 3. Non-Functional Requirements

### 3.1 Performance

| ID | Requirement | Target |
|----|------------|--------|
| NFR-01 | API response time | < 500ms |
| NFR-02 | Frontend page load | < 3s |
| NFR-03 | Dashboard data refresh | < 5s |

### 3.2 Scalability

| ID | Requirement | Target |
|----|------------|--------|
| NFR-04 | Docker Compose deployment | Single-host |
| NFR-05 | Nginx reverse proxy | Port 80 (external) |
| NFR-06 | API port | 8000 |
| NFR-07 | Frontend port | 3000 |

### 3.3 Reliability

| ID | Requirement | Target |
|----|------------|--------|
| NFR-08 | DuckDB database file persistence | Volume mount |
| NFR-09 | Graceful null/undefined handling | Required |
| NFR-10 | Zero-downtime redeploys via Docker | When possible |

### 3.4 Compatibility

| ID | Requirement | Target |
|----|------------|--------|
| NFR-11 | Next.js version | 15.1.3+ |
| NFR-12 | FastAPI version | Latest stable |
| NFR-13 | Nginx version | 1.31.4+ |
| NFR-14 | DuckDB version | Latest stable |

## 4. Reference Implementation Context

From Armoyas/analytical-dashboard:

1. **Docker Compose services**:
   - api (FastAPI + DuckDB + uvicorn) on port 8000
   - frontend (Next.js 15.1.3 standalone output) on port 3000
   - nginx (reverse proxy) on port 80

2. **Build fixes applied**:
   - Next.js 14.2.5 → 15.1.3 (fixes prerendering error on `/dashboard`)
   - `force-dynamic` in next.config.js + `cache: false` in docker-compose.yml
   - `MerchantSelector.tsx`: `(merchants || []).find()` null-safety fix
   - Docker build: `docker compose build --no-cache`

3. **Deployment target**:
   - Host: 62.60.198.209 (SSH filtered, HTTP healthy)

4. **ZarrinPal schema**:
   - `merchant_key` (string): Unique merchant identifier
   - `session_status` (string): Payment session status
   - `amount` (integer): Transaction amount in IRR (Rials)
   - `adjusted_fee` (integer): Adjusted fee amount

## 5. Acceptance Criteria

- [ ] All Stage 0 specification files created and committed
- [ ] Repository is public on GitHub (Armoyas/dashboard)
- [ ] README.md references the specification-driven approach
- [ ] Requirements traceability to reference repo established
- [ ] Technology stack explicitly defined
- [ ] All stakeholder roles identified
- [ ] Success criteria measurable and documented
