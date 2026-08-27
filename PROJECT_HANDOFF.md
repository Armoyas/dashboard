# PROJECT HANDOFF

> Repository: Armoyas/dashboard
> Reference: Armoyas/analytical-dashboard
> Stage: Stage 0 — Project Definition Complete

## Executive Summary

A spec-driven development dashboard application for ZarrinPal payment analytics, built upon the reference architecture from Armoyas/analytical-dashboard. This document consolidates all Stage 0 specifications for project handoff.

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Name** | dashboard |
| **Purpose** | SDD-based dashboard using spec-driven development methodology |
| **Visibility** | Public |
| **Reference** | Armoyas/analytical-dashboard |
| **Methodology** | Spec-Driven Development (SDD) with Speckit approach |

## Architecture

Three-tier deployment via Docker Compose:

```
Internet → Nginx (80) → Next.js Frontend (3000) / FastAPI API (8000) → DuckDB
```

| Component | Technology | Port |
|-----------|------------|------|
| Reverse Proxy | Nginx 1.31.4+ | 80 |
| Frontend | Next.js 15.1.3+ (standalone) | 3000 |
| Backend | FastAPI + uvicorn | 8000 |
| Database | DuckDB | N/A |

## ZarrinPal Data Schema

| Field | Type | Description |
|-------|------|-------------|
| `merchant_key` | string | Unique merchant identifier |
| `session_status` | string | Payment session status |
| `amount` | integer | Transaction amount in IRR (Rials) |
| `adjusted_fee` | integer | Adjusted fee amount |

## Key Requirements

### Functional
- FR-01: Dashboard summary statistics ✓
- FR-02: Transaction data with filters ✓
- FR-03: API endpoints ✓
- FR-04: Next.js server-side rendering ✓

### Non-Functional
- NFR-01: API response < 500ms
- NFR-02: Page load < 3s
- NFR-11: Next.js 15.1.3+ (avoids prerendering errors)

## Reference Repo Constraints (from analytical-dashboard)

1. Next.js 15.1.3+ (fixes `/dashboard` prerendering error)
2. `force-dynamic` in next.config.js
3. Null-safety pattern: `(merchants || []).find()`
4. Build: `docker compose build --no-cache`
5. Deployment: 62.60.198.209 (SSH filtered, HTTP healthy)

## Stage 0 Deliverables

All files created and committed to Armoyas/dashboard:

| File | Status |
|------|--------|
| README.md | ✓ |
| LICENSE | ✓ |
| .gitignore | ✓ |
| specs/stage0/README.md | ✓ |
| specs/stage0/constitution.md | ✓ |
| specs/stage0/requirements.md | ✓ |
| specs/stage0/architecture.md | ✓ |
| specs/stage0/api-contract.md | ✓ |
| PROJECT_HANDOFF.md | ✓ (this file) |

## Next Steps

- **Stage 1**: Expand requirements, select detailed tech stack, define component specs
- **Implementation**: Build Docker Compose services, API endpoints, frontend components
- **Testing**: Verify against reference repo patterns and null-safety fixes

## Approval

Stage 0 specifications are ready for review. Upon approval, proceed to Stage 1.
