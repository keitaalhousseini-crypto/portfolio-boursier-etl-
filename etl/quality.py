
import numpy as np

from etl.config import EXPECTED_SYMBOLS, DATA_SOURCE


def validate_prices(df):
    results = {}

    required = [
        "price_date", "symbol", "open", "high",
        "low", "close", "adj_close", "volume",
        "data_source", "daily_return",
    ]

    results["required_columns"] = int(
        len(set(required) - set(df.columns)) == 0
    )

    if not results["required_columns"]:
        raise ValueError("Colonnes obligatoires manquantes")

    results["duplicate_keys"] = int(
        df.duplicated(["symbol", "price_date"]).sum()
    )

    results["missing_dates"] = int(
        df["price_date"].isna().sum()
    )

    results["missing_prices"] = int(
        df[["open", "high", "low", "close", "adj_close"]]
        .isna().sum().sum()
    )

    prices = ["open", "high", "low", "close", "adj_close"]

    results["invalid_prices"] = int(
        (df[prices] <= 0).sum().sum()
    )

    results["invalid_ohlc"] = int((
        (df["high"] < df[["open", "close", "low"]].max(axis=1))
        |
        (df["low"] > df[["open", "close", "high"]].min(axis=1))
    ).sum())

    results["invalid_volumes"] = int(
        (
            df["volume"].isna()
            | (df["volume"] < 0)
            | (df["volume"] % 1 != 0)
        ).sum()
    )

    results["invalid_returns"] = int(
        (
            ~np.isfinite(
                df["daily_return"].dropna().to_numpy(
                    dtype=float
                )
            )
        ).sum()
    )

    results["invalid_symbols"] = int(
        (~df["symbol"].isin(EXPECTED_SYMBOLS)).sum()
    )

    results["invalid_sources"] = int(
        (df["data_source"] != DATA_SOURCE).sum()
    )

    errors = {
        key: value
        for key, value in results.items()
        if key != "required_columns" and value != 0
    }

    if errors:
        raise ValueError(
            f"Contrôles qualité échoués : {errors}"
        )

    print("[QUALITY] Tous les contrôles bloquants : OK")
    print(f"[QUALITY] Doublons : {results['duplicate_keys']}")

    return results
