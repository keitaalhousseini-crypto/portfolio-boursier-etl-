
CREATE OR REPLACE VIEW finance.v_asset_summary AS

WITH latest_returns AS (
    SELECT DISTINCT ON (symbol)
        symbol,
        price_date AS last_price_date,
        adj_close AS last_adjusted_close,
        cumulative_return_pct
    FROM finance.v_asset_returns
    ORDER BY symbol, price_date DESC
),

maximum_drawdowns AS (
    SELECT
        symbol,
        MIN(drawdown_pct) AS max_drawdown_pct
    FROM finance.v_asset_drawdown
    GROUP BY symbol
)

SELECT
    r.symbol,
    r.last_price_date,
    r.last_adjusted_close,
    r.cumulative_return_pct,
    v.annual_volatility_pct,
    d.max_drawdown_pct,
    s.sharpe_ratio,
    s.annualized_mean_return_pct

FROM latest_returns r

JOIN finance.v_asset_volatility v
    ON r.symbol = v.symbol

JOIN maximum_drawdowns d
    ON r.symbol = d.symbol

JOIN finance.v_asset_sharpe s
    ON r.symbol = s.symbol;
