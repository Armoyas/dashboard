-- ZarrinPal Analytics Dashboard Database Schema
-- Based on the reference analytical-dashboard schema

-- Merchants table
CREATE TABLE IF NOT EXISTS merchants (
    merchant_key VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table (core ZarrinPal payment data)
CREATE TABLE IF NOT EXISTS sessions (
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

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    status VARCHAR,
    amount BIGINT,
    fee BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_merchant_key ON sessions(merchant_key);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(session_status);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_sessions_amount ON sessions(amount);
