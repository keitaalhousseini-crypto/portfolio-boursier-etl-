
-- Table séparée pour les cours boursiers réels
CREATE TABLE IF NOT EXISTS finance.market_prices_real (
    symbol VARCHAR(20) NOT NULL,
    price_date DATE NOT NULL,

    open NUMERIC(18, 6) NOT NULL,
    high NUMERIC(18, 6) NOT NULL,
    low NUMERIC(18, 6) NOT NULL,
    close NUMERIC(18, 6) NOT NULL,
    adj_close NUMERIC(18, 6) NOT NULL,

    volume BIGINT NOT NULL,

    data_source VARCHAR(30) NOT NULL
        DEFAULT 'YAHOO_FINANCE',

    downloaded_at_utc TIMESTAMPTZ NOT NULL,

    CONSTRAINT pk_market_prices_real
        PRIMARY KEY (symbol, price_date),

    CONSTRAINT chk_real_source
        CHECK (data_source = 'YAHOO_FINANCE'),

    CONSTRAINT chk_real_prices
        CHECK (
            open > 0
            AND high > 0
            AND low > 0
            AND close > 0
            AND adj_close > 0
        ),

    CONSTRAINT chk_real_volume
        CHECK (volume >= 0),

    CONSTRAINT chk_real_ohlc
        CHECK (
            high >= low
            AND high >= open
            AND high >= close
            AND low <= open
            AND low <= close
        )
);

CREATE INDEX IF NOT EXISTS idx_market_prices_real_date
ON finance.market_prices_real(price_date);
