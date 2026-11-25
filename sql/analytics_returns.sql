
CREATE OR REPLACE VIEW finance.v_asset_returns AS

WITH prices AS (
    SELECT
        symbol,
        price_date,
        adj_close,

        LAG(adj_close) OVER (
            PARTITION BY symbol
            ORDER BY price_date
        ) AS previous_close,

        FIRST_VALUE(adj_close) OVER (
            PARTITION BY symbol
            ORDER BY price_date
        ) AS first_close

    FROM finance.market_prices_real
)

SELECT
    symbol,
    price_date,
    adj_close,

    ROUND(
        100.0 * (adj_close / NULLIF(previous_close, 0) - 1),
        4
    ) AS daily_return_pct,

    ROUND(
        100.0 * (adj_close / NULLIF(first_close, 0) - 1),
        4
    ) AS cumulative_return_pct

FROM prices;
