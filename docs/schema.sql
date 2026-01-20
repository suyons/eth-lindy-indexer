-- PostgreSQL Schema for ETH Lindy Indexer

-- 1. Blocks Table
CREATE TABLE IF NOT EXISTS blocks (
    number BIGINT PRIMARY KEY,
    hash VARCHAR(66) UNIQUE NOT NULL,
    parent_hash VARCHAR(66) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    miner VARCHAR(42) NOT NULL,
    difficulty NUMERIC(78, 0) NOT NULL,
    total_difficulty NUMERIC(78, 0) NOT NULL,
    size INTEGER NOT NULL,
    extra_data TEXT NOT NULL,
    gas_limit BIGINT NOT NULL,
    gas_used BIGINT NOT NULL,
    base_fee_per_gas BIGINT
);

CREATE INDEX IF NOT EXISTS idx_blocks_hash ON blocks(hash);
CREATE INDEX IF NOT EXISTS idx_blocks_parent_hash ON blocks(parent_hash);
CREATE INDEX IF NOT EXISTS idx_blocks_number ON blocks(number);

-- 2. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    hash VARCHAR(66) PRIMARY KEY,
    nonce INTEGER NOT NULL,
    block_hash VARCHAR(66) NOT NULL,
    block_number BIGINT NOT NULL REFERENCES blocks(number) ON DELETE CASCADE,
    transaction_index INTEGER NOT NULL,
    from_address VARCHAR(42) NOT NULL,
    to_address VARCHAR(42),
    value NUMERIC(78, 0) NOT NULL,
    gas_price BIGINT NOT NULL,
    gas BIGINT NOT NULL,
    input TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_transactions_block_hash ON transactions(block_hash);
CREATE INDEX IF NOT EXISTS idx_transactions_block_number ON transactions(block_number);
CREATE INDEX IF NOT EXISTS idx_transactions_from_address ON transactions(from_address);
CREATE INDEX IF NOT EXISTS idx_transactions_to_address ON transactions(to_address);

-- 3. Logs Table
CREATE TABLE IF NOT EXISTS logs (
    id BIGSERIAL PRIMARY KEY,
    log_index INTEGER NOT NULL,
    transaction_hash VARCHAR(66) NOT NULL REFERENCES transactions(hash) ON DELETE CASCADE,
    address VARCHAR(42) NOT NULL,
    data TEXT NOT NULL,
    topics JSONB NOT NULL,
    block_number BIGINT NOT NULL REFERENCES blocks(number) ON DELETE CASCADE,
    block_hash VARCHAR(66) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_logs_transaction_hash ON logs(transaction_hash);
CREATE INDEX IF NOT EXISTS idx_logs_block_number ON logs(block_number);
CREATE INDEX IF NOT EXISTS idx_logs_address ON logs(address);
CREATE INDEX IF NOT EXISTS idx_logs_block_hash ON logs(block_hash);
