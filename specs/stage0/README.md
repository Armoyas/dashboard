# SDD Stage 0: Project Definition

> Reference Repository: Armoyas/analytical-dashboard
> New Repository: Armoyas/dashboard

## 1. Project Identity

| Attribute | Value |
|-----------|-------|
| **Name** | dashboard |
| **Purpose** | SDD-based dashboard using spec-driven development methodology |
| **Visibility** | Public |
| **Reference** | Armoyas/analytical-dashboard |
| **Methodology** | Spec-Driven Development (SDD) with Speckit approach |

## 2. High-Level Architecture

| Component | Technology | Port | Description |
|-----------|------------|------|-------------|
| **API** | FastAPI + uvicorn | 8000 | RESTful API serving analytics data |
| **Frontend** | Next.js 15.1.3 (standalone output) | 3000 | React-based dashboard UI with SSR |
| **Database** | DuckDB | N/A | Analytics database with ZarrinPal schema |
| **Proxy** | Nginx 1.31.4 | 80 | Reverse proxy for frontend and API |

## 3. Data Model Reference (from reference repo)

Based on analytical-dashboard schema (ZarrinPal analytics):

| Field | Type | Description |
|-------|------|-------------|
| `merchant_key` | string | Unique merchant identifier |
| `session_status` | string | Payment session status |
| `amount` | integer | Transaction amount in IRR (Rials) |
| `adjusted_fee` | integer | Adjusted fee amount |

## 4. Stage 0 Deliverables

1. README.md (this file)
2. specs/stage0/README.md
3. specs/stage0/constitution.md
4. specs/stage0/requirements.md
5. specs/stage0/architecture.md
6. specs/stage0/api-contract.md
7. .gitignore
8. LICENSE

## 5. Next Stage: Stage 1

Stage 1 will expand:
- Detailed requirements
- Component specifications
- Technology stack selection
- Deployment configuration

## 6. Reference Repo Context

The reference repository (Armoyas/analytical-dashboard) includes:
- Next.js 15.1.3 with standalone output
- FastAPI backend with DuckDB
- ZarrinPal analytics dashboard
- Nginx reverse proxy configuration
- Docker Compose deployment
- Deployment target: 62.60.198.209

## 7. Constraints & Assumptions

- Build on reference repo's Docker Compose structure
- Use Next.js 15.1.3+ to avoid prerendering errors
- Apply null-safety patterns (e.g., `(merchants || []).find()`)
- Maintain ZarrinPal schema compatibility
- Stage 0 specs must be reviewed before advancing to Stage 1
