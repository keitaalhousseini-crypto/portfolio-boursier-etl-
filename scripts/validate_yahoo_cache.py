
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "data/raw/market_prices_yahoo.csv"

EXPECTED_SYMBOLS = {
    "AAPL", "MSFT", "NVDA", "AMZN",
    "GOOGL", "JPM", "UBS", "SPY"
}

REQUIRED_COLUMNS = {
    "date", "symbol", "open", "high",
    "low", "close", "adj_close", "volume",
    "data_source", "downloaded_at_utc"
}


def validate_cache():
    print("===== VALIDATION CACHE YAHOO =====")

    if not FILE.exists():
        raise FileNotFoundError(f"Fichier absent : {FILE}")

    df = pd.read_csv(FILE)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    assert not missing_columns, (
        f"Colonnes manquantes : {missing_columns}"
    )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    price_columns = [
        "open", "high", "low", "close", "adj_close"
    ]

    for column in price_columns + ["volume"]:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    duplicate_count = df.duplicated(
        subset=["symbol", "date"]
    ).sum()

    missing_count = df[
        ["date", "symbol"] + price_columns + ["volume"]
    ].isna().sum().sum()

    invalid_prices = (
        df[price_columns].le(0).any(axis=1)
    ).sum()

    invalid_volume = (df["volume"] < 0).sum()

    invalid_ohlc = (
        (df["high"] < df["low"])
        | (df["high"] < df["open"])
        | (df["high"] < df["close"])
        | (df["low"] > df["open"])
        | (df["low"] > df["close"])
    ).sum()

    unknown_symbols = (
        set(df["symbol"].dropna()) - EXPECTED_SYMBOLS
    )

    invalid_sources = (
        df["data_source"] != "YAHOO_FINANCE"
    ).sum()

    invalid_download_dates = pd.to_datetime(
        df["downloaded_at_utc"],
        errors="coerce",
        utc=True,
    ).isna().sum()

    print(f"Lignes : {len(df)}")
    print(f"Actifs : {df['symbol'].nunique()}")
    print(f"Doublons : {duplicate_count}")
    print(f"Valeurs manquantes : {missing_count}")
    print(f"Prix invalides : {invalid_prices}")
    print(f"Volumes invalides : {invalid_volume}")
    print(f"OHLC incohérents : {invalid_ohlc}")
    print(f"Symboles inconnus : {unknown_symbols}")
    print(f"Sources invalides : {invalid_sources}")
    print(f"Dates téléchargement invalides : {invalid_download_dates}")

    assert len(df) > 0, "Fichier vide"
    assert set(df["symbol"]) == EXPECTED_SYMBOLS
    assert duplicate_count == 0
    assert missing_count == 0
    assert invalid_prices == 0
    assert invalid_volume == 0
    assert invalid_ohlc == 0
    assert not unknown_symbols
    assert invalid_sources == 0
    assert invalid_download_dates == 0

    print("\n[SUCCESS] Cache Yahoo Finance valide")


if __name__ == "__main__":
    validate_cache()
