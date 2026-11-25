
CREATE OR REPLACE VIEW finance.v_asset_drawdown AS

WITH price_peaks AS (
    SELECT
        symbol,
        price_date,
        adj_close,

        MAX(adj_close) OVER (
            PARTITION BY symbol
            ORDER BY price_date
            ROWS BETWEEN UNBOUNDED PRECEDING
                     AND CURRENT ROW
        ) AS running_peak

    FROM finance.market_prices_real
),

drawdowns AS (
    SELECT
        symbol,
        price_date,
        adj_close,
        running_peak,

        ROUND(
            (
                100.0 * (
                    adj_close / NULLIF(running_peak, 0) - 1
                )
            )::NUMERIC,
            4
        ) AS drawdown_pct

    FROM price_peaks
)

SELECT *
FROM drawdowns;


-- 1. Créer la vue du Maximum Drawdown

CREATE OR REPLACE VIEW finance.v_asset_drawdown AS

WITH price_peaks AS (
    SELECT
        symbol,
        price_date,
        adj_close,

        MAX(adj_close) OVER (
            PARTITION BY symbol
            ORDER BY price_date
            ROWS BETWEEN UNBOUNDED PRECEDING
                     AND CURRENT ROW
        ) AS running_peak

    FROM finance.market_prices_real
)

SELECT
    symbol,
    price_date,
    adj_close,
    running_peak,

    ROUND(
        100.0 * (
            adj_close / NULLIF(running_peak, 0) - 1
        ),
        4
    ) AS drawdown_pct

FROM price_peaks;


-- 2. Vérifier que la vue existe

SELECT
    to_regclass('finance.v_asset_drawdown')
        AS vue_creee;


-- 3. Calculer le Maximum Drawdown

SELECT
    symbol,
    MIN(drawdown_pct) AS max_drawdown_pct
FROM finance.v_asset_drawdown
GROUP BY symbol
ORDER BY max_drawdown_pct;
