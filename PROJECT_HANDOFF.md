# PROJECT_HANDOFF.md

## Project: dashboard
An SDD-methodology analytical dashboard for ZarrinPal payment data, built on the Armoyas/analytical-dashboard reference.

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
- **Backend**: FastAPI + uvicorn on port 8000
- **Database**: DuckDB with ZarrinPal payment schema
- **Proxy**: Nginx with Docker Compose

## Server
- Host: 62.60.198.209
- Ports: 80 (nginx), 3000 (frontend), 8000 (backend)

## Stages
- **Stage 0**: High-level requirements and architecture ✓
- **Stage 1**: Detailed component specs and API contracts ✓

## Files
| File | Purpose |
|------|---------|
| specs/stage0/constitution.md | Project scope and principles |
| specs/stage0/requirements.md | Functional/non-functional requirements |
| specs/stage0/architecture.md | Architecture diagram and decisions |
| specs/stage0/api-contract.md | API endpoint definitions |
| specs/stage1/components.md | Component-level breakdown |
| specs/stage1/api-specs.md | Detailed API specifications |
| specs/stage1/database.md | Database schema and queries |
| specs/stage1/deployment.md | Deployment and rollback procedures |
| specs/stage1/testing.md | Testing strategy and CI/CD |
