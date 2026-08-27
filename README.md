# Dashboard

A spec-driven development (SDD) dashboard application for ZarrinPal payment analytics, built upon the architectural patterns from [Armoyas/analytical-dashboard](https://github.com/Armoyas/analytical-dashboard).

## Methodology

This project follows the **Spec-Driven Development (SDD)** methodology using the **Speckit** approach. All specifications are defined in the `specs/` directory before implementation.

### Spec Structure

```
specs/
└── stage0/
    ├── README.md           # Stage 0 overview
    ├── constitution.md     # Project constitution
    ├── requirements.md     # Functional & non-functional requirements
    ├── architecture.md     # High-level architecture
    └── api-contract.md     # API endpoint definitions
```

## Architecture

```
Internet → Nginx (80) → Next.js Frontend (3000) / FastAPI API (8000) → DuckDB
```

| Component | Technology | Purpose |
|-----------|------------|---------|
| Reverse Proxy | Nginx 1.31.4 | Routing & static assets |
| Frontend | Next.js 15.1.3 | Dashboard UI |
| Backend | FastAPI | Analytics API |
| Database | DuckDB | ZarrinPal transaction data |

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/Armoyas/dashboard.git
cd dashboard

# Review Stage 0 specifications
ls specs/stage0/

# Build and run (after Stage 1 implementation)
docker compose up --build
```

## Data Schema

The dashboard uses the ZarrinPal analytics schema:

| Field | Type | Description |
|-------|------|-------------|
| `merchant_key` | string | Unique merchant identifier |
| `session_status` | string | Payment session status |
| `amount` | integer | Transaction amount in IRR (Rials) | 
| `adjusted_fee` | integer | Adjusted fee amount |

## Reference

- **Reference Repository**: [Armoyas/analytical-dashboard](https://github.com/Armoyas/analytical-dashboard)
- **Deployment**: Host 62.60.198.209 (ports 80, 3000, 8000)

## License

MIT License - see [LICENSE](LICENSE) file.
