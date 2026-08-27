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

-- Insert sample data for testing
INSERT OR IGNORE INTO merchants (merchant_key, name) VALUES
('test_merchant_001', 'Test Merchant One'),
('test_merchant_002', 'Test Merchant Two');

INSERT OR IGNORE INTO sessions (id, merchant_key, session_status, amount, adjusted_fee, authority, email, mobile) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'test_merchant_001', 'SUCCESS', 500000, 15000, 'auth123', 'user1@test.com', '09120000001'),
('b2c3d4e5-f6a7-8901-bcde-f1234567890', 'test_merchant_002', 'FAILED', 300000, 9000, 'auth456', 'user2@test.com', '09120000002'),
('c3d4e5f6-a7b8-9012-cdef-12345678901', 'test_merchant_001', 'SUCCESS', 750000, 22500, 'auth789', 'user3@test.com', '09120000003');