# Stage 1: API Endpoint Specifications

## Base Information
- **Base URL**: `http://62.60.198.209/api/`
- **Protocol**: HTTP/HTTPS
- **Authentication**: Not required (internal analytics dashboard)

## Endpoints

### Health Check
```
GET /api/health
```
**Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### List Merchants
```
GET /api/merchants
```
**Response (200 OK)**:
```json
{
  "merchants": [
    {
      "merchant_key": "abc123xyz",
      "name": "Merchant Name",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Get Analytics Overview
```
GET /api/analytics/overview?from=2025-01-01&to=2025-01-31
```
**Query Parameters**:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| from | string (date) | Optional | Start date |
| to | string (date) | Optional | End date |
| merchant_key | string | Optional | Filter by merchant |

**Response (200 OK)**:
```json
{
  "total_revenue": 1500000000,
  "total_transactions": 2450,
  "success_rate": 0.95,
  "avg_transaction": 6122449,
  "merchants_count": 3,
  "date_range": {
    "from": "2025-01-01",
    "to": "2025-01-31"
  }
}
```

### Get Merchant Analytics
```
GET /api/analytics/merchant/{merchant_key}
```
**Path Parameters**:
| Param | Type | Description |
|-------|------|-------------|
| merchant_key | string | Unique merchant identifier |

**Response (200 OK)**:
```json
{
  "merchant_key": "abc123xyz",
  "name": "Merchant Name",
  "total_revenue": 500000000,
  "total_sessions": 850,
  "success_sessions": 820,
  "success_rate": 0.965,
  "avg_amount": 5882353,
  "recent_sessions": [
    {
      "session_id": "uuid-here",
      "status": "completed",
      "amount": 1500000,
      "created_at": "2025-01-31T15:45:00Z"
    }
  ]
}
```

### List Sessions
```
GET /api/sessions?status=paid&limit=100&offset=0
```
**Query Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| status | string | optional | Filter by status |
| merchant_key | string | optional | Filter by merchant |
| limit | integer | 100 | Results limit |
| offset | integer | 0 | Pagination offset |

**Response (200 OK)**:
```json
{
  "sessions": [
    {
      "id": "uuid-here",
      "merchant_key": "abc123xyz",
      "session_status": "paid",
      "amount": 2500000,
      "adjusted_fee": 50000,
      "authority": "A123456789",
      "email": "user@example.com",
      "mobile": "09123456789",
      "created_at": "2025-01-31T15:45:00Z"
    }
  ],
  "total": 2450,
  "limit": 100,
  "offset": 0
}
```

### Error Responses

#### 404 Not Found
```json
{
  "error": "Resource not found",
  "details": "Merchant with key 'invalid-key' not found"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "Database query failed",
  "timestamp": "2025-01-31T15:45:00Z"
}
```
