
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf


# Configuration
SYMBOLS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "JPM", "UBS", "SPY"]

START_DATE = "2020-01-01"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "data" / "raw"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = CACHE_DIR / "market_prices_yahoo.csv"


def download_prices():
    frames = []

    for symbol in SYMBOLS:
        print(f"[DOWNLOAD] {symbol}")

        try:
            ticker = yf.Ticker(symbol)

            df = ticker.history(
                start=START_DATE,
                interval="1d",
                auto_adjust=False,
                timeout=20,
            )

            if df.empty:
                print(f"[WARNING] Aucune donnée pour {symbol}")
                continue

            df = df.reset_index()

            # Normaliser les noms de colonnes
            df.columns = [
                str(column).lower().replace(" ", "_")
                for column in df.columns
            ]

            # Conserver la date sans fuseau horaire
            df["date"] = pd.to_datetime(
                df["date"]
            ).dt.date.astype(str)

            df["symbol"] = symbol
            df["data_source"] = "YAHOO_FINANCE"
            df["downloaded_at_utc"] = (
                datetime.now(timezone.utc).isoformat()
            )

            columns = [
                "date",
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "adj_close",
                "volume",
                "data_source",
                "downloaded_at_utc",
            ]

            df = df[columns]
            frames.append(df)

            print(f"[SUCCESS] {symbol} : {len(df)} lignes")

        except Exception as error:
            print(f"[ERROR] {symbol} : {error}")

    if not frames:
        print("[ECHEC] Aucun téléchargement réussi")
        return

    final_df = pd.concat(frames, ignore_index=True)

    # Ne jamais conserver des doublons
    final_df = final_df.drop_duplicates(
        subset=["symbol", "date"],
        keep="last",
    )

    final_df = final_df.sort_values(
        ["symbol", "date"]
    ).reset_index(drop=True)

    # Écriture atomique : ne remplacer le cache
    # qu'une fois le fichier entièrement écrit
    temporary_file = CACHE_FILE.with_suffix(".tmp")
    final_df.to_csv(temporary_file, index=False)
    temporary_file.replace(CACHE_FILE)

    print("\n===== RESULTAT =====")
    print(f"Nombre de lignes : {len(final_df)}")
    print(f"Nombre d'actifs : {final_df['symbol'].nunique()}")
    print(f"Fichier : {CACHE_FILE}")
    print(f"Source : YAHOO_FINANCE")


if __name__ == "__main__":
    download_prices()
