
CREATE SCHEMA IF NOT EXISTS finance;

CREATE TABLE IF NOT EXISTS finance.assets (
    symbol VARCHAR(12) PRIMARY KEY,
    asset_name VARCHAR(100) NOT NULL,
    sector VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS finance.etl_runs (
    run_id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
    data_mode VARCHAR(20) NOT NULL,
    data_source VARCHAR(50) NOT NULL,
    rows_extracted INTEGER NOT NULL DEFAULT 0,
    rows_loaded INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    CONSTRAINT valid_run_status CHECK (
        status IN ('RUNNING', 'SUCCESS', 'FAILED')
    )
);

CREATE TABLE IF NOT EXISTS finance.market_prices (
    symbol VARCHAR(12) NOT NULL
        REFERENCES finance.assets(symbol),
    price_date DATE NOT NULL,
    open_price NUMERIC(20,6) NOT NULL,
    high_price NUMERIC(20,6) NOT NULL,
    low_price NUMERIC(20,6) NOT NULL,
    close_price NUMERIC(20,6) NOT NULL,
    adj_close NUMERIC(20,6) NOT NULL,
    volume BIGINT NOT NULL,
    daily_return DOUBLE PRECISION,
    ma_20 DOUBLE PRECISION,
    volatility_20 DOUBLE PRECISION,
    is_anomaly BOOLEAN NOT NULL DEFAULT FALSE,
    data_source VARCHAR(50) NOT NULL,
    run_id BIGINT REFERENCES finance.etl_runs(run_id),

    PRIMARY KEY (symbol, price_date),

    CONSTRAINT valid_prices CHECK (
        open_price > 0
        AND high_price > 0
        AND low_price > 0
        AND close_price > 0
        AND adj_close > 0
        AND high_price >= open_price
        AND high_price >= close_price
        AND low_price <= open_price
        AND low_price <= close_price
    ),

    CONSTRAINT valid_volume CHECK (volume >= 0)
);

CREATE INDEX IF NOT EXISTS idx_market_prices_date
ON finance.market_prices(price_date);

CREATE INDEX IF NOT EXISTS idx_market_prices_source
ON finance.market_prices(data_source);

CREATE TABLE IF NOT EXISTS finance.portfolio_positions (
    position_id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(12) NOT NULL
        REFERENCES finance.assets(symbol),
    quantity NUMERIC(20,6) NOT NULL,
    purchase_price NUMERIC(20,6) NOT NULL,
    purchase_date DATE NOT NULL,
    CONSTRAINT valid_quantity CHECK (quantity > 0),
    CONSTRAINT valid_purchase_price CHECK (purchase_price > 0)
);

CREATE TABLE IF NOT EXISTS finance.portfolio_performance (
    valuation_date DATE NOT NULL,
    symbol VARCHAR(12) NOT NULL
        REFERENCES finance.assets(symbol),
    quantity NUMERIC(20,6) NOT NULL,
    market_value NUMERIC(20,6) NOT NULL,
    daily_return DOUBLE PRECISION,
    PRIMARY KEY (valuation_date, symbol)
);

CREATE TABLE IF NOT EXISTS finance.data_quality_logs (
    log_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL
        REFERENCES finance.etl_runs(run_id),
    check_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    observed_value INTEGER,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
