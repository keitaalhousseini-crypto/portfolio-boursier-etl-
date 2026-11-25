
from sqlalchemy import text

from etl.config import get_engine


def test_transaction_rollback():
    engine = get_engine()

    try:
        with engine.connect() as conn:
            # Mesurer le nombre initial dans une transaction
            with conn.begin() as transaction:
                before = conn.execute(text("""
                    SELECT COUNT(*)
                    FROM finance.assets
                """)).scalar_one()

                conn.execute(text("""
                    INSERT INTO finance.assets (
                        symbol, asset_name, sector
                    )
                    VALUES (
                        'TESTROLL',
                        'Rollback Test Asset',
                        'Testing'
                    )
                """))

                inside = conn.execute(text("""
                    SELECT COUNT(*)
                    FROM finance.assets
                    WHERE symbol = 'TESTROLL'
                """)).scalar_one()

                assert inside == 1

                # Annuler explicitement la transaction
                transaction.rollback()

            # Nouvelle transaction implicite de lecture
            after = conn.execute(text("""
                SELECT COUNT(*)
                FROM finance.assets
            """)).scalar_one()

            remaining = conn.execute(text("""
                SELECT COUNT(*)
                FROM finance.assets
                WHERE symbol = 'TESTROLL'
            """)).scalar_one()

            assert before == after
            assert remaining == 0

    finally:
        engine.dispose()
