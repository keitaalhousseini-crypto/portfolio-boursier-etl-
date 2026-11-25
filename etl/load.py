
import math

import pandas as pd
from sqlalchemy import text

from etl.config import ASSET_INFO, DATA_SOURCE


INSERT_PRICE = text("""
INSERT INTO finance.market_prices (
    symbol, price_date, open_price, high_price,
    low_price, close_price, adj_close, volume,
    daily_return, ma_20, volatility_20,
    is_anomaly, data_source, run_id
)
VALUES (
    :symbol, :price_date, :open_price, :high_price,
    :low_price, :close_price, :adj_close, :volume,
    :daily_return, :ma_20, :volatility_20,
    :is_anomaly, :data_source, :run_id
)
ON CONFLICT (symbol, price_date)
DO UPDATE SET
    open_price = EXCLUDED.open_price,
    high_price = EXCLUDED.high_price,
    low_price = EXCLUDED.low_price,
    close_price = EXCLUDED.close_price,
    adj_close = EXCLUDED.adj_close,
    volume = EXCLUDED.volume,
    daily_return = EXCLUDED.daily_return,
    ma_20 = EXCLUDED.ma_20,
    volatility_20 = EXCLUDED.volatility_20,
    is_anomaly = EXCLUDED.is_anomaly,
    run_id = EXCLUDED.run_id
WHERE finance.market_prices.data_source = EXCLUDED.data_source
""")


def clean_value(value):
    if value is None:
        return None

    if isinstance(value, float) and not math.isfinite(value):
        return None

    if pd.isna(value):
        return None

    return value


def prepare_records(df, run_id):
    records = []

    for row in df.to_dict(orient="records"):
        records.append({
            "symbol": row["symbol"],
            "price_date": row["price_date"],
            "open_price": clean_value(row["open"]),
            "high_price": clean_value(row["high"]),
            "low_price": clean_value(row["low"]),
            "close_price": clean_value(row["close"]),
            "adj_close": clean_value(row["adj_close"]),
            "volume": int(row["volume"]),
            "daily_return": clean_value(row["daily_return"]),
            "ma_20": clean_value(row["ma_20"]),
            "volatility_20": clean_value(row["volatility_20"]),
            "is_anomaly": bool(row["is_anomaly"]),
            "data_source": row["data_source"],
            "run_id": run_id,
        })

    return records


def load_prices(engine, df, run_id, quality_results):
    records = prepare_records(df, run_id)

    with engine.begin() as conn:
        # Interdit le mélange de sources.
        existing_sources = conn.execute(text("""
            SELECT DISTINCT data_source
            FROM finance.market_prices
        """)).scalars().all()

        if any(source != DATA_SOURCE for source in existing_sources):
            raise ValueError(
                "Une autre source existe déjà dans market_prices. "
                "Chargement annulé pour éviter le mélange."
            )

        for symbol, (name, sector) in ASSET_INFO.items():
            conn.execute(text("""
                INSERT INTO finance.assets
                    (symbol, asset_name, sector)
                VALUES (:symbol, :name, :sector)
                ON CONFLICT (symbol)
                DO UPDATE SET
                    asset_name = EXCLUDED.asset_name,
                    sector = EXCLUDED.sector
            """), {
                "symbol": symbol,
                "name": name,
                "sector": sector,
            })

        batch_size = 1000

        for start in range(0, len(records), batch_size):
            batch = records[start:start + batch_size]
            conn.execute(INSERT_PRICE, batch)

        for check_name, observed_value in quality_results.items():
            conn.execute(text("""
                INSERT INTO finance.data_quality_logs (
                    run_id, check_name, status, observed_value
                )
                VALUES (:run_id, :name, 'PASS', :value)
            """), {
                "run_id": run_id,
                "name": check_name,
                "value": observed_value,
            })

        conn.execute(text("""
            UPDATE finance.etl_runs
            SET status = 'SUCCESS',
                finished_at = NOW(),
                rows_loaded = :rows_loaded
            WHERE run_id = :run_id
        """), {
            "rows_loaded": len(records),
            "run_id": run_id,
        })

    print(f"[LOAD] {len(records)} lignes traitées")
    print("[LOAD] Transaction validée")

    return len(records)
