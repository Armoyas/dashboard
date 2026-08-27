# Stage 1: Database Schema

## Overview
Uses DuckDB as the analytical database engine for storing ZarrinPal payment data.

## Schema Diagram
```
merchants
├── merchant_key (PK)
├── name
└── created_at

sessions
├── id (PK)
├── merchant_key (FK → merchants)
├── session_status
├── amount (Rials)
├── adjusted_fee
├── authority
├── email
├── mobile
├── created_at
└── updated_at

transactions
├── id (PK)
├── session_id (FK → sessions)
├── status
├── amount
├── fee
└── created_at
```

## Tables

### merchants
Stores merchant account information from ZarrinPal.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| merchant_key | VARCHAR | PK, NOT NULL | Unique identifier from ZarrinPal |
| name | VARCHAR | | Human-readable merchant name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### sessions
Core ZarrinPal payment session data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique session identifier |
| merchant_key | VARCHAR | FK → merchants, NOT NULL | Links to merchant account |
| session_status | VARCHAR | NOT NULL | Payment status (paid, expired, canceled) |
| amount | BIGINT | NOT NULL | Transaction amount in Rials (IRR) |
| adjusted_fee | BIGINT | | Processing fee amount |
| authority | VARCHAR | UNIQUE | ZarrinPal transaction authority code |
| email | VARCHAR | | Payer email |
| mobile | VARCHAR | | Payer mobile number |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Session creation |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update |

### transactions
Individual transactions linked to sessions (for future extension).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique transaction ID |
| session_id | UUID | FK → sessions | Links to parent session |
| status | VARCHAR | NOT NULL | Transaction status |
| amount | BIGINT | NOT NULL | Amount in Rials |
| fee | BIGINT | | Transaction fee |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Transaction timestamp |

## Indexes
```sql
CREATE INDEX idx_sessions_merchant_key ON sessions(merchant_key);
CREATE INDEX idx_sessions_status ON sessions(session_status);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_amount ON sessions(amount);
CREATE INDEX idx_merchants_name ON merchants(name);
```

## Sample SQL Queries

### Revenue by Merchant
```sql
SELECT 
    m.name AS merchant_name,
    COUNT(s.id) AS total_sessions,
    SUM(s.amount) AS total_revenue_rials,
    ROUND(AVG(s.amount), 0) AS avg_amount_rials
FROM sessions s
JOIN merchants m ON s.merchant_key = m.merchant_key
WHERE s.session_status = 'paid'
GROUP BY m.merchant_key, m.name
ORDER BY total_revenue_rials DESC;
```

### Daily Transaction Volume
```sql
SELECT 
    DATE(created_at) AS day,
    COUNT(*) AS transaction_count,
    SUM(amount) AS daily_volume_rials
FROM sessions
WHERE session_status = 'paid'
GROUP BY DATE(created_at)
ORDER BY day DESC;
```

### Success Rate Over Time
```sql
SELECT 
    DATE_TRUNC('month', created_at) AS month,
    session_status,
    COUNT(*) AS count
FROM sessions
GROUP BY DATE_TRUNC('month', created_at), session_status
ORDER BY month DESC;
```

## Data Import Notes
- Amounts stored in Rials (IRR) - no decimal places needed
- `adjusted_fee` may differ from standard ZarrinPal fee structure
- `merchant_key` is the only identifier from ZarrinPal (no customer_id or product_id)
