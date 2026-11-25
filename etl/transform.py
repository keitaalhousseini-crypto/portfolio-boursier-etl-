
import numpy as np
import pandas as pd


def transform_prices(df):
    df = df.copy()

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    required = [
        "date", "symbol", "sector",
        "open", "high", "low", "close",
        "adj_close", "volume", "data_source",
    ]

    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(
            f"Colonnes manquantes : {sorted(missing)}"
        )

    df["date"] = pd.to_datetime(
        df["date"], errors="coerce"
    )

    numeric_columns = [
        "open", "high", "low",
        "close", "adj_close", "volume",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    # Les doublons strictement identiques sont supprimés.
    df = df.drop_duplicates()

    df = df.sort_values(
        ["symbol", "date"]
    ).reset_index(drop=True)

    grouped = df.groupby("symbol", sort=False)

    df["daily_return"] = grouped["adj_close"].pct_change(
        fill_method=None
    )

    df["ma_20"] = grouped["adj_close"].transform(
        lambda s: s.rolling(
            window=20, min_periods=20
        ).mean()
    )

    df["volatility_20"] = grouped["daily_return"].transform(
        lambda s: s.rolling(
            window=20, min_periods=20
        ).std() * np.sqrt(252)
    )

    df["is_anomaly"] = (
        df["daily_return"].abs() > 0.15
    ).fillna(False)

    df["price_date"] = df["date"].dt.date

    print(f"[TRANSFORM] {len(df)} lignes transformées")

    return df
