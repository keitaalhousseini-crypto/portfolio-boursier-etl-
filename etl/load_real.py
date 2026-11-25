
from sqlalchemy import text

from etl.config import get_engine
from etl.data_source import load_market_data


UPSERT_SQL = text("""
    INSERT INTO finance.market_prices_real (
        symbol,
        price_date,
        open,
        high,
        low,
        close,
        adj_close,
        volume,
        data_source,
        downloaded_at_utc
    )
    VALUES (
        :symbol,
        :price_date,
        :open,
        :high,
        :low,
        :close,
        :adj_close,
        :volume,
        :data_source,
        :downloaded_at_utc
    )
    ON CONFLICT (symbol, price_date)
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        adj_close = EXCLUDED.adj_close,
        volume = EXCLUDED.volume,
        data_source = EXCLUDED.data_source,
        downloaded_at_utc = EXCLUDED.downloaded_at_utc
""")


def load_real_prices():
    print("===== CHARGEMENT YAHOO FINANCE =====")

    # CACHE impose l'utilisation des données réelles.
    # Aucun basculement silencieux vers DEMO.
    df, mode = load_market_data("CACHE")

    if mode != "CACHE":
        raise ValueError("Source réelle obligatoire")

    df = df.rename(columns={"date": "price_date"})

    # Conversion des dates pour PostgreSQL
    df["price_date"] = df["price_date"].dt.date

    df["downloaded_at_utc"] = (
        df["downloaded_at_utc"].astype(str)
    )

    columns = [
        "symbol",
        "price_date",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
        "data_source",
        "downloaded_at_utc",
    ]

    records = df[columns].to_dict(orient="records")

    engine = get_engine()

    try:
        # Une seule transaction :
        # toutes les lignes sont chargées ou aucune.
        with engine.begin() as conn:
            batch_size = 500

            for start in range(0, len(records), batch_size):
                batch = records[start:start + batch_size]
                conn.execute(UPSERT_SQL, batch)

            total = conn.execute(text("""
                SELECT COUNT(*)
                FROM finance.market_prices_real
            """)).scalar_one()

            print(f"[SUCCESS] Lignes réelles en base : {total}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    load_real_prices()
