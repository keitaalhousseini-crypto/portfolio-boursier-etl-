
from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

CACHE_FILE = ROOT / "data/raw/market_prices_yahoo.csv"
DEMO_FILE = ROOT / "data/demo/market_prices_demo.csv"

SYMBOLS = {
    "AAPL", "MSFT", "NVDA", "AMZN",
    "GOOGL", "JPM", "UBS", "SPY"
}


def read_validated_file(path, expected_source):
    """Lire un CSV et vérifier sa qualité minimale."""

    df = pd.read_csv(path)

    required = {
        "date", "symbol", "open", "high", "low",
        "close", "adj_close", "volume", "data_source"
    }

    if not required.issubset(df.columns):
        raise ValueError("Colonnes obligatoires manquantes")

    if df.empty:
        raise ValueError("Fichier vide")

    if set(df["symbol"].dropna()) != SYMBOLS:
        raise ValueError("Liste des actifs incorrecte")

    if not df["data_source"].eq(expected_source).all():
        raise ValueError("Provenance incorrecte")

    df["date"] = pd.to_datetime(
        df["date"], errors="coerce"
    )

    if df["date"].isna().any():
        raise ValueError("Dates invalides")

    if df.duplicated(["symbol", "date"]).any():
        raise ValueError("Doublons détectés")

    numeric_columns = [
        "open", "high", "low", "close",
        "adj_close", "volume"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    if df[numeric_columns].isna().any().any():
        raise ValueError("Valeurs numériques manquantes")

    if df[
        ["open", "high", "low", "close", "adj_close"]
    ].le(0).any().any():
        raise ValueError("Prix invalides")

    if (df["volume"] < 0).any():
        raise ValueError("Volumes négatifs")

    if (
        (df["high"] < df["low"])
        | (df["high"] < df["open"])
        | (df["high"] < df["close"])
        | (df["low"] > df["open"])
        | (df["low"] > df["close"])
    ).any():
        raise ValueError("OHLC incohérents")

    return df


def load_market_data(mode="AUTO"):
    """
    AUTO  : cache réel valide, sinon démo.
    CACHE : cache réel uniquement.
    DEMO  : données synthétiques uniquement.

    Aucun téléchargement Internet.
    Aucun chargement PostgreSQL.
    """

    mode = mode.upper()

    if mode not in {"AUTO", "CACHE", "DEMO"}:
        raise ValueError(f"Mode inconnu : {mode}")

    if mode in {"AUTO", "CACHE"}:
        try:
            df = read_validated_file(
                CACHE_FILE, "YAHOO_FINANCE"
            )

            print("[SOURCE] CACHE")
            print("[PROVENANCE] YAHOO_FINANCE")
            return df, "CACHE"

        except (FileNotFoundError, ValueError) as error:
            if mode == "CACHE":
                raise

            print(f"[WARNING] Cache indisponible : {error}")

    df = read_validated_file(
        DEMO_FILE, "SYNTHETIC_DEMO"
    )

    print("[SOURCE] DEMO")
    print("[PROVENANCE] SYNTHETIC_DEMO")

    return df, "DEMO"
