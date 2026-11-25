
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from etl.data_source import load_market_data


print("===== TEST MODE AUTO =====")
df, mode = load_market_data("AUTO")

print(f"Mode sélectionné : {mode}")
print(f"Nombre de lignes : {len(df)}")
print(f"Nombre d'actifs : {df['symbol'].nunique()}")
print(f"Provenance : {df['data_source'].unique()}")

print("\n===== TEST MODE DEMO =====")
demo, demo_mode = load_market_data("DEMO")

print(f"Mode sélectionné : {demo_mode}")
print(f"Nombre de lignes : {len(demo)}")

print("\n===== FIN DES TESTS =====")
