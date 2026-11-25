
from pathlib import Path
import argparse

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "demo" / "market_prices_demo.csv"

ASSETS = {
    "AAPL": {"price": 75.0, "mu": 0.0005, "sigma": 0.020, "sector": "Technology"},
    "MSFT": {"price": 160.0, "mu": 0.0005, "sigma": 0.018, "sector": "Technology"},
    "NVDA": {"price": 6.0, "mu": 0.0007, "sigma": 0.035, "sector": "Technology"},
    "AMZN": {"price": 95.0, "mu": 0.0004, "sigma": 0.023, "sector": "Consumer Discretionary"},
    "GOOGL": {"price": 70.0, "mu": 0.0004, "sigma": 0.021, "sector": "Communication Services"},
    "JPM": {"price": 135.0, "mu": 0.0003, "sigma": 0.019, "sector": "Financials"},
    "UBS": {"price": 12.0, "mu": 0.0003, "sigma": 0.022, "sector": "Financials"},
    "SPY": {"price": 320.0, "mu": 0.0003, "sigma": 0.012, "sector": "ETF"},
}


def generate_data(
    start="2020-01-01",
    end="2025-12-31",
    seed=42,
):
    """Génère des cours synthétiques OHLCV reproductibles."""

    rng = np.random.default_rng(seed)

    dates = pd.bdate_range(start=start, end=end)
    if len(dates) < 2:
        raise ValueError("La période doit contenir au moins deux jours ouvrés.")

    # Facteur commun : crée une corrélation entre les actifs.
    market_returns = rng.normal(
        loc=0.00025,
        scale=0.009,
        size=len(dates),
    )

    frames = []

    for symbol, params in ASSETS.items():
        specific_returns = rng.normal(
            loc=params["mu"],
            scale=params["sigma"],
            size=len(dates),
        )

        log_returns = 0.65 * market_returns + specific_returns

        close = params["price"] * np.exp(
            np.cumsum(log_returns)
        )

        # Le cours d'ouverture est proche de la clôture précédente.
        previous_close = np.concatenate(
            ([params["price"]], close[:-1])
        )

        open_price = previous_close * np.exp(
            rng.normal(0, 0.004, size=len(dates))
        )

        # High et Low encadrent toujours Open et Close.
        upper_spread = rng.uniform(0.001, 0.025, len(dates))
        lower_spread = rng.uniform(0.001, 0.025, len(dates))

        high = np.maximum(open_price, close) * (1 + upper_spread)
        low = np.minimum(open_price, close) * (1 - lower_spread)

        volume = rng.integers(
            low=500_000,
            high=15_000_000,
            size=len(dates),
        )

        frame = pd.DataFrame({
            "date": dates,
            "symbol": symbol,
            "sector": params["sector"],
            "open": np.round(open_price, 4),
            "high": np.round(high, 4),
            "low": np.round(low, 4),
            "close": np.round(close, 4),
            "adj_close": np.round(close, 4),
            "volume": volume,
            "data_source": "SYNTHETIC_DEMO",
        })

        frames.append(frame)

    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values(
        ["symbol", "date"]
    ).reset_index(drop=True)

    return df


def validate_data(df):
    """Vérifie les principales règles de qualité."""

    required = {
        "date", "symbol", "open", "high", "low",
        "close", "adj_close", "volume", "data_source",
    }

    if not required.issubset(df.columns):
        raise ValueError("Colonnes obligatoires manquantes")

    if df.duplicated(["symbol", "date"]).any():
        raise ValueError("Doublons symbole/date")

    prices = ["open", "high", "low", "close", "adj_close"]

    if df[prices].isna().any().any():
        raise ValueError("Prix manquants")

    if (df[prices] <= 0).any().any():
        raise ValueError("Prix négatifs ou nuls")

    if (df["volume"] < 0).any():
        raise ValueError("Volumes négatifs")

    if (df["high"] < df[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("Prix High incohérent")

    if (df["low"] > df[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("Prix Low incohérent")

    if not df["data_source"].eq("SYNTHETIC_DEMO").all():
        raise ValueError("Source synthétique non identifiée")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Générateur de cours boursiers synthétiques"
    )
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    print("=== MODE DEMO : DONNEES SYNTHETIQUES ===")
    print("Ces cours ne sont PAS des cours réels.")

    df = generate_data(
        start=args.start,
        end=args.end,
        seed=args.seed,
    )

    validate_data(df)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, date_format="%Y-%m-%d")

    print("Fichier :", OUTPUT)
    print("Observations :", len(df))
    print("Actifs :", df["symbol"].nunique())
    print("Dates :", df["date"].min(), "→", df["date"].max())
    print("Source :", df["data_source"].unique().tolist())
    print("Qualité : OK")


if __name__ == "__main__":
    main()
