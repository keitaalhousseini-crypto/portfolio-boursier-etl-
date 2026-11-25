
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")

DEMO_FILE = ROOT / "data" / "demo" / "market_prices_demo.csv"

DATA_MODE = "DEMO"
DATA_SOURCE = "SYNTHETIC_DEMO"

EXPECTED_SYMBOLS = {
    "AAPL", "MSFT", "NVDA", "AMZN",
    "GOOGL", "JPM", "UBS", "SPY",
}

ASSET_INFO = {
    "AAPL": ("Apple", "Technology"),
    "MSFT": ("Microsoft", "Technology"),
    "NVDA": ("Nvidia", "Technology"),
    "AMZN": ("Amazon", "Consumer Discretionary"),
    "GOOGL": ("Alphabet", "Communication Services"),
    "JPM": ("JPMorgan Chase", "Financials"),
    "UBS": ("UBS Group", "Financials"),
    "SPY": ("SPDR S&P 500 ETF", "ETF"),
}


def get_engine():
    password = os.getenv("POSTGRES_PASSWORD")

    if not password or password == "CHANGE_ME":
        raise ValueError(
            "Configure POSTGRES_PASSWORD dans .env"
        )

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER", "portfolio_admin"),
        password=password,
        host="127.0.0.1",
        port=int(os.getenv("POSTGRES_PORT", "55432")),
        database=os.getenv("POSTGRES_DB", "portfolio_db"),
    )

    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )
