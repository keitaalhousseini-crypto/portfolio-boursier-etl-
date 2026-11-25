
from etl.extract import extract_demo


def test_demo_extraction():
    df = extract_demo()

    assert len(df) == 12528
    assert df["symbol"].nunique() == 8
    assert set(df["data_source"]) == {"SYNTHETIC_DEMO"}
