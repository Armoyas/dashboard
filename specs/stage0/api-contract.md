# API Contract (Stage 0 Draft)

> Reference Repository: Armoyas/analytical-dashboard
> New Repository: Armoyas/dashboard
> Stage: Stage 0

## 1. API Overview

The dashboard API is built with FastAPI and provides endpoints for ZarrinPal payment analytics data.

## 2. Base URL

```
http://localhost:8000/api
```

## 3. Endpoints

### 3.1 Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-08-27T10:00:00Z"
}
```

### 3.2 Get All Transactions

```
GET /transactions
```

Query Parameters:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `merchant_key` | string | No | Filter by merchant key |
| `session_status` | string | No | Filter by session status |
| `limit` | integer | No | Maximum number of results (default: 100) |
| `offset` | integer | No | Pagination offset (default: 0) |

Response:
```json
{
  "transactions": [
    {
      "id": 1,
      "merchant_key": "merchant_abc123",
      "session_status": "completed",
      "amount": 500000,
      "adjusted_fee": 15000,
      "created_at": "2026-08-27T09:00:00Z"
    }
  ],
  "count": 1,
  "total": 1000
}
```

### 3.3 Get Merchant Summary

```
GET /merchants/{merchant_key}/summary
```

Response:
```json
{
  "merchant_key": "merchant_abc123",
  "total_transactions": 1500,
  "total_amount": 750000000,
  "status_breakdown": {
    "completed": 1200,
    "failed": 200,
    "pending": 100
  }
}
```

## 4. Data Schema

### 4.1 Transaction Model

```json
{
  "id": "integer (primary key)",
  "merchant_key": "string (foreign key to merchants)",
  "session_status": "string (enum: completed, failed, pending)",
  "amount": "integer (IRR, Rials)",
  "adjusted_fee": "integer (IRR, Rials)",
  "created_at": "timestamp (ISO 8601)"
}
```

### 4.2 Merchant Model

```json
{
  "merchant_key": "string (primary key)",
  "name": "string",
  "created_at": "timestamp (ISO 8601)"
}
```

## 5. Reference Repo Endpoints (from Armoyas/analytical-dashboard)

Based on reference implementation:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/transactions` | List transactions |
| GET | `/api/merchants` | List all merchants |
| GET | `/api/merchants/{key}` | Get merchant details |
| GET | `/api/stats/summary` | Get overall summary statistics |

## 6. Notes for Future Stages

- Stage 1 will define complete endpoint specifications
- OpenAPI/Swagger documentation will be auto-generated
- Rate limiting considerations will be added in Stage 1
- Authentication requirements to be defined in Stage 1
