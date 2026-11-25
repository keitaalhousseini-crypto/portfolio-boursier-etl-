
from etl.extract import extract_demo
from etl.transform import transform_prices


def test_transform_columns():
    df = transform_prices(extract_demo())

    expected = {
        "price_date",
        "daily_return",
        "ma_20",
        "volatility_20",
        "is_anomaly",
    }

    assert expected.issubset(df.columns)


def test_first_daily_return_is_null():
    df = transform_prices(extract_demo())

    first_rows = df.groupby("symbol").head(1)

    assert first_rows["daily_return"].isna().all()
