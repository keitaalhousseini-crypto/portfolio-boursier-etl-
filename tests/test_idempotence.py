
import subprocess
import sys

from sqlalchemy import text

from etl.config import ROOT, get_engine


def database_state(engine):
    """Lire l'état actuel de la base."""
    with engine.connect() as conn:
        total = conn.execute(text("""
            SELECT COUNT(*)
            FROM finance.market_prices
        """)).scalar_one()

        unique_keys = conn.execute(text("""
            SELECT COUNT(DISTINCT (symbol, price_date))
            FROM finance.market_prices
        """)).scalar_one()

        runs = conn.execute(text("""
            SELECT COUNT(*)
            FROM finance.etl_runs
        """)).scalar_one()

    return total, unique_keys, runs


def test_pipeline_is_idempotent():
    engine = get_engine()

    try:
        # État avant exécution
        before_total, before_unique, before_runs = (
            database_state(engine)
        )

        assert before_total == 12528
        assert before_unique == before_total

        # Relancer le véritable pipeline ETL
        result = subprocess.run(
            [sys.executable, "-m", "etl.pipeline"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        assert result.returncode == 0, (
            result.stdout + "\n" + result.stderr
        )

        # État après exécution
        after_total, after_unique, after_runs = (
            database_state(engine)
        )

        # Aucun nouveau cours en double
        assert after_total == before_total
        assert after_unique == after_total

        # Une nouvelle exécution enregistrée
        assert after_runs == before_runs + 1

        # La dernière exécution est réussie
        with engine.connect() as conn:
            latest_status = conn.execute(text("""
                SELECT status
                FROM finance.etl_runs
                ORDER BY run_id DESC
                LIMIT 1
            """)).scalar_one()

        assert latest_status == "SUCCESS"

    finally:
        engine.dispose()
