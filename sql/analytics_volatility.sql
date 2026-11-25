
CREATE OR REPLACE VIEW finance.v_asset_volatility AS

SELECT
    symbol,

    COUNT(daily_return_pct) AS observations,

    ROUND(
        AVG(daily_return_pct),
        4
    ) AS average_daily_return_pct,

    ROUND(
        STDDEV_SAMP(daily_return_pct),
        4
    ) AS daily_volatility_pct,

    ROUND(
        STDDEV_SAMP(daily_return_pct)
        * SQRT(252),
        4
    ) AS annual_volatility_pct

FROM finance.v_asset_returns

WHERE daily_return_pct IS NOT NULL

GROUP BY symbol;
