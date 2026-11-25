
from pathlib import Path

import pytest

import etl.data_source as source


def test_auto_uses_real_cache():
    """AUTO privilégie le cache Yahoo valide."""
    df, mode = source.load_market_data("AUTO")

    assert mode == "CACHE"
    assert len(df) == 13872
    assert set(df["data_source"]) == {"YAHOO_FINANCE"}


def test_demo_mode():
    """DEMO utilise les données synthétiques."""
    df, mode = source.load_market_data("DEMO")

    assert mode == "DEMO"
    assert len(df) == 12528
    assert set(df["data_source"]) == {"SYNTHETIC_DEMO"}


def test_auto_fallback_when_cache_missing(monkeypatch, tmp_path):
    """AUTO bascule vers DEMO si le cache est absent."""

    missing_cache = tmp_path / "cache_inexistant.csv"

    monkeypatch.setattr(
        source,
        "CACHE_FILE",
        missing_cache,
    )

    df, mode = source.load_market_data("AUTO")

    assert mode == "DEMO"
    assert len(df) == 12528
    assert set(df["data_source"]) == {"SYNTHETIC_DEMO"}


def test_cache_mode_fails_when_missing(monkeypatch, tmp_path):
    """CACHE refuse de remplacer silencieusement
    des données réelles par des données synthétiques.
    """

    missing_cache = tmp_path / "cache_inexistant.csv"

    monkeypatch.setattr(
        source,
        "CACHE_FILE",
        missing_cache,
    )

    with pytest.raises(FileNotFoundError):
        source.load_market_data("CACHE")


def test_invalid_mode_rejected():
    """Un mode inconnu doit être refusé."""

    with pytest.raises(ValueError, match="Mode inconnu"):
        source.load_market_data("UNKNOWN")
