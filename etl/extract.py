
import pandas as pd

from etl.config import DEMO_FILE


def extract_demo():
    if not DEMO_FILE.is_file():
        raise FileNotFoundError(
            f"Fichier absent : {DEMO_FILE}\n"
            "Lance : python scripts/generate_demo_data.py"
        )

    df = pd.read_csv(DEMO_FILE)

    if df.empty:
        raise ValueError("Le fichier CSV est vide.")

    print(f"[EXTRACT] {len(df)} lignes lues")
    print("[EXTRACT] Source : SYNTHETIC_DEMO")

    return df
