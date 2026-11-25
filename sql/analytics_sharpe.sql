
CREATE OR REPLACE VIEW finance.v_asset_sharpe AS

WITH metrics AS (
    SELECT
        symbol,
        COUNT(daily_return_pct) AS observations,

        AVG(daily_return_pct) AS avg_daily_pct,

        STDDEV_SAMP(daily_return_pct) AS std_daily_pct

    FROM finance.v_asset_returns

    WHERE daily_return_pct IS NOT NULL

    GROUP BY symbol
)

SELECT
    symbol,
    observations,

    ROUND(
        (avg_daily_pct * 252)::NUMERIC,
        4
    ) AS annualized_mean_return_pct,

    ROUND(
        (std_daily_pct * SQRT(252))::NUMERIC,
        4
    ) AS annualized_volatility_pct,

    ROUND(
        (
            (avg_daily_pct * 252 - 2.0)
            / NULLIF(std_daily_pct * SQRT(252), 0)
        )::NUMERIC,
        4
    ) AS sharpe_ratio

FROM metrics;
