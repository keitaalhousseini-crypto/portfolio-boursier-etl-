
import pytest

from etl.extract import extract_demo
from etl.transform import transform_prices
from etl.quality import validate_prices


def test_valid_demo_data():
    df = transform_prices(extract_demo())
    results = validate_prices(df)

    assert results["duplicate_keys"] == 0
    assert results["invalid_prices"] == 0
    assert results["invalid_volumes"] == 0


def test_duplicate_detection():
    df = transform_prices(extract_demo())

    duplicate = df.iloc[[0]]
    df = __import__("pandas").concat(
        [df, duplicate], ignore_index=True
    )

    with pytest.raises(ValueError, match="duplicate_keys"):
        validate_prices(df)


def test_negative_volume_detection():
    df = transform_prices(extract_demo())
    df.loc[0, "volume"] = -100

    with pytest.raises(ValueError, match="invalid_volumes"):
        validate_prices(df)
