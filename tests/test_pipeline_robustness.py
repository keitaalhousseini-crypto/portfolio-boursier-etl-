
import pandas as pd
import pytest

from etl.extract import extract_demo
from etl.transform import transform_prices
from etl.quality import validate_prices


@pytest.fixture
def valid_data():
    """Données synthétiques transformées."""
    return transform_prices(extract_demo())


def test_missing_price_rejected(valid_data):
    """Refuser un prix manquant."""
    df = valid_data.copy()
    df.loc[0, "close"] = None

    with pytest.raises(ValueError, match="missing_prices"):
        validate_prices(df)


def test_negative_price_rejected(valid_data):
    """Refuser un prix négatif."""
    df = valid_data.copy()
    df.loc[0, "close"] = -100

    with pytest.raises(ValueError, match="invalid_prices"):
        validate_prices(df)


def test_inconsistent_ohlc_rejected(valid_data):
    """Refuser un prix haut inférieur au prix bas."""
    df = valid_data.copy()
    df.loc[0, "high"] = df.loc[0, "low"] - 1

    with pytest.raises(ValueError, match="invalid_ohlc"):
        validate_prices(df)


def test_unknown_symbol_rejected(valid_data):
    """Refuser un symbole inconnu."""
    df = valid_data.copy()
    df.loc[0, "symbol"] = "UNKNOWN"

    with pytest.raises(ValueError, match="invalid_symbols"):
        validate_prices(df)


def test_real_source_rejected(valid_data):
    """Empêcher le mélange données réelles/synthétiques."""
    df = valid_data.copy()
    df.loc[0, "data_source"] = "YAHOO_FINANCE"

    with pytest.raises(ValueError, match="invalid_sources"):
        validate_prices(df)
