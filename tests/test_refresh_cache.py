
import pandas as pd
import pytest

import scripts.refresh_yahoo_cache as refresh


def test_recent_cache_skips_download(monkeypatch):
    """Un cache récent évite tout téléchargement."""

    monkeypatch.setattr(
        refresh, "cache_is_fresh", lambda: True
    )

    def forbidden_download():
        raise AssertionError(
            "Le téléchargement ne devait pas être appelé"
        )

    monkeypatch.setattr(
        refresh, "download_all", forbidden_download
    )

    refresh.refresh_cache()


def test_download_failure_preserves_cache(
    monkeypatch, tmp_path
):
    """Une panne réseau ne doit pas détruire le cache."""

    cache = tmp_path / "market_prices_yahoo.csv"
    cache.write_text("ANCIEN_CACHE", encoding="utf-8")

    monkeypatch.setattr(refresh, "CACHE_FILE", cache)
    monkeypatch.setattr(
        refresh, "cache_is_fresh", lambda: False
    )

    def failed_download():
        raise RuntimeError("Panne Yahoo simulée")

    monkeypatch.setattr(
        refresh, "download_all", failed_download
    )

    with pytest.raises(
        RuntimeError, match="Panne Yahoo simulée"
    ):
        refresh.refresh_cache()

    assert cache.read_text(
        encoding="utf-8"
    ) == "ANCIEN_CACHE"


def test_incomplete_download_preserves_cache(
    monkeypatch, tmp_path
):
    """Un téléchargement incomplet ne remplace pas le cache."""

    cache = tmp_path / "market_prices_yahoo.csv"
    cache.write_text("ANCIEN_CACHE", encoding="utf-8")

    monkeypatch.setattr(refresh, "CACHE_FILE", cache)
    monkeypatch.setattr(
        refresh, "cache_is_fresh", lambda: False
    )

    incomplete = pd.DataFrame({
        "date": ["2026-11-24"],
        "symbol": ["AAPL"],
        "open": [100.0],
        "high": [105.0],
        "low": [99.0],
        "close": [102.0],
        "adj_close": [102.0],
        "volume": [1000],
        "data_source": ["YAHOO_FINANCE"],
        "downloaded_at_utc": [
            "2026-11-24T12:00:00+00:00"
        ],
    })

    monkeypatch.setattr(
        refresh, "download_all", lambda: incomplete
    )

    with pytest.raises(ValueError):
        refresh.refresh_cache()

    assert cache.read_text(
        encoding="utf-8"
    ) == "ANCIEN_CACHE"
