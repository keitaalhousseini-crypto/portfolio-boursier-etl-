
from datetime import datetime, timezone
from pathlib import Path
import os
import sys

import pandas as pd
import yfinance as yf

from etl.data_source import (
    CACHE_FILE,
    SYMBOLS,
    read_validated_file,
)


MAX_AGE_HOURS = 24
START_DATE = "2020-01-01"


def cache_is_fresh():
    """Vérifier que le cache est valide et récent."""

    if not CACHE_FILE.exists():
        return False

    try:
        df = read_validated_file(
            CACHE_FILE, "YAHOO_FINANCE"
        )

        if "downloaded_at_utc" not in df.columns:
            return False

        timestamps = pd.to_datetime(
            df["downloaded_at_utc"],
            utc=True,
            errors="coerce",
        )

        if timestamps.isna().any():
            return False

        now = pd.Timestamp.now(tz="UTC")
        age_hours = (
            now - timestamps.min()
        ).total_seconds() / 3600

        if age_hours < 0:
            return False

        print(f"[CACHE] Age : {age_hours:.1f} heures")

        return age_hours < MAX_AGE_HOURS

    except (ValueError, OSError, pd.errors.ParserError):
        return False


def download_all():
    """Télécharger les huit actifs sans modifier le cache."""

    frames = []
    downloaded_at = datetime.now(
        timezone.utc
    ).isoformat()

    for symbol in sorted(SYMBOLS):
        print(f"[DOWNLOAD] {symbol}")

        try:
            df = yf.Ticker(symbol).history(
                start=START_DATE,
                interval="1d",
                auto_adjust=False,
                timeout=20,
            )

            if df.empty:
                raise ValueError("Réponse vide")

            df = df.reset_index()

            df.columns = [
                str(col).lower().replace(" ", "_")
                for col in df.columns
            ]

            df["date"] = pd.to_datetime(
                df["date"]
            ).dt.date.astype(str)

            df["symbol"] = symbol
            df["data_source"] = "YAHOO_FINANCE"
            df["downloaded_at_utc"] = downloaded_at

            columns = [
                "date", "symbol", "open", "high",
                "low", "close", "adj_close",
                "volume", "data_source",
                "downloaded_at_utc",
            ]

            df = df[columns]
            frames.append(df)

            print(f"[SUCCESS] {symbol}: {len(df)} lignes")

        except Exception as error:
            raise RuntimeError(
                f"Téléchargement incomplet pour {symbol}: {error}"
            ) from error

    result = pd.concat(frames, ignore_index=True)

    if set(result["symbol"]) != SYMBOLS:
        raise ValueError("Certains actifs sont absents")

    if result.duplicated(["symbol", "date"]).any():
        raise ValueError("Doublons détectés")

    return result.sort_values(
        ["symbol", "date"]
    ).reset_index(drop=True)


def refresh_cache():
    """Remplacer le cache uniquement après validation."""

    print("===== RAFRAICHISSEMENT YAHOO =====")

    if cache_is_fresh():
        print("[SKIP] Cache récent et valide")
        return

    print("[INFO] Téléchargement nécessaire")

    temporary_file = CACHE_FILE.with_name(
        CACHE_FILE.name + ".tmp"
    )

    try:
        new_data = download_all()

        # Sauvegarde temporaire
        new_data.to_csv(temporary_file, index=False)

        # Validation avec le même contrôleur
        validated = read_validated_file(
            temporary_file, "YAHOO_FINANCE"
        )

        if len(validated) != len(new_data):
            raise ValueError("Nombre de lignes incohérent")

        if validated["symbol"].nunique() != len(SYMBOLS):
            raise ValueError("Actifs manquants")

        # Ne pas remplacer par un historique raccourci
        if CACHE_FILE.exists():
            try:
                old = read_validated_file(
                    CACHE_FILE, "YAHOO_FINANCE"
                )

                old_keys = set(zip(
                    old["symbol"], old["date"].dt.date
                ))
                new_keys = set(zip(
                    validated["symbol"],
                    validated["date"].dt.date
                ))

                if not old_keys.issubset(new_keys):
                    raise ValueError(
                        "Le téléchargement perd des dates "
                        "présentes dans l'ancien cache"
                    )

            except (
                OSError,
                pd.errors.ParserError,
            ):
                # Ancien fichier illisible :
                # le nouveau a déjà été validé.
                pass

        # Remplacement atomique
        os.replace(temporary_file, CACHE_FILE)

        print("[SUCCESS] Cache actualisé")
        print(f"Lignes : {len(validated)}")
        print(f"Actifs : {validated['symbol'].nunique()}")
        print(f"Fichier : {CACHE_FILE}")

    except Exception as error:
        print(f"[ERROR] {error}")
        print("[SAFE] Cache précédent conservé")
        raise

    finally:
        temporary_file.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        refresh_cache()
    except Exception:
        sys.exit(1)
