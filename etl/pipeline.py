
import logging
from datetime import datetime, timezone

from sqlalchemy import text

from etl.config import (
    ROOT,
    DATA_MODE,
    DATA_SOURCE,
    get_engine,
)
from etl.extract import extract_demo
from etl.transform import transform_prices
from etl.quality import validate_prices
from etl.load import load_prices


LOG_FILE = ROOT / "logs" / "etl.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def create_run(engine, rows_extracted):
    with engine.begin() as conn:
        run_id = conn.execute(text("""
            INSERT INTO finance.etl_runs (
                data_mode, data_source, rows_extracted
            )
            VALUES (:mode, :source, :rows)
            RETURNING run_id
        """), {
            "mode": DATA_MODE,
            "source": DATA_SOURCE,
            "rows": rows_extracted,
        }).scalar_one()

    return run_id


def mark_failed(engine, run_id, message):
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE finance.etl_runs
            SET status = 'FAILED',
                finished_at = NOW(),
                error_message = :message
            WHERE run_id = :run_id
        """), {
            "run_id": run_id,
            "message": str(message)[:2000],
        })


def main():
    logger.info("===== DEMARRAGE ETL =====")
    logger.info("Mode : %s", DATA_MODE)
    logger.info("Source : %s", DATA_SOURCE)

    engine = None
    run_id = None

    try:
        df_raw = extract_demo()
        df_clean = transform_prices(df_raw)
        quality_results = validate_prices(df_clean)

        engine = get_engine()

        with engine.connect() as conn:
            database = conn.execute(
                text("SELECT current_database()")
            ).scalar_one()

        logger.info("Base connectée : %s", database)

        run_id = create_run(engine, len(df_raw))

        rows = load_prices(
            engine,
            df_clean,
            run_id,
            quality_results,
        )

        logger.info("Lignes traitées : %s", rows)
        logger.info("Run ID : %s", run_id)
        logger.info("Statut : SUCCESS")

    except Exception:
        logger.exception("ECHEC DU PIPELINE")

        if engine is not None and run_id is not None:
            try:
                mark_failed(
                    engine,
                    run_id,
                    "Échec du chargement ETL. Voir logs/etl.log",
                )
            except Exception:
                logger.exception(
                    "Impossible de journaliser l'échec"
                )

        raise

    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    main()
