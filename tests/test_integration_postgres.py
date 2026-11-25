
import pytest
from sqlalchemy import text

from etl.config import get_engine


@pytest.fixture(scope="module")
def engine():
    """Connexion PostgreSQL utilisée par les tests."""
    db_engine = get_engine()

    yield db_engine

    db_engine.dispose()


def test_database_connection(engine):
    """Vérifier que Python accède à la bonne base."""
    with engine.connect() as conn:
        database = conn.execute(
            text("SELECT current_database()")
        ).scalar_one()

    assert database == "portfolio_db"


def test_finance_tables_exist(engine):
    """Vérifier la présence des six tables."""
    expected = {
        "assets",
        "market_prices",
        "portfolio_positions",
        "portfolio_performance",
        "etl_runs",
        "data_quality_logs",
    }

    with engine.connect() as conn:
        tables = set(conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'finance'
        """)).scalars())

    assert expected.issubset(tables)


def test_market_prices_count(engine):
    """Vérifier le nombre de cours chargés."""
    with engine.connect() as conn:
        count = conn.execute(text("""
            SELECT COUNT(*)
            FROM finance.market_prices
        """)).scalar_one()

    assert count == 12528


def test_no_duplicate_prices(engine):
    """Vérifier l'unicité symbole/date."""
    with engine.connect() as conn:
        duplicates = conn.execute(text("""
            SELECT COUNT(*)
            FROM (
                SELECT symbol, price_date
                FROM finance.market_prices
                GROUP BY symbol, price_date
                HAVING COUNT(*) > 1
            ) AS duplicates
        """)).scalar_one()

    assert duplicates == 0


def test_only_synthetic_source(engine):
    """Empêcher le mélange des sources."""
    with engine.connect() as conn:
        sources = set(conn.execute(text("""
            SELECT DISTINCT data_source
            FROM finance.market_prices
        """)).scalars())

    assert sources == {"SYNTHETIC_DEMO"}


def test_latest_etl_success(engine):
    """Vérifier le dernier statut ETL."""
    with engine.connect() as conn:
        status = conn.execute(text("""
            SELECT status
            FROM finance.etl_runs
            ORDER BY run_id DESC
            LIMIT 1
        """)).scalar_one()

    assert status == "SUCCESS"


def test_eight_assets(engine):
    """Vérifier les huit actifs financiers."""
    with engine.connect() as conn:
        count = conn.execute(text("""
            SELECT COUNT(*)
            FROM finance.assets
        """)).scalar_one()

    assert count == 8
