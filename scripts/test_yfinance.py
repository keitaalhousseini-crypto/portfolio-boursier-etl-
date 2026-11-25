
import yfinance as yf

SYMBOL = "AAPL"

print("===== TEST YAHOO FINANCE =====")
print(f"yfinance version : {yf.__version__}")
print(f"Symbole : {SYMBOL}")

try:
    ticker = yf.Ticker(SYMBOL)

    df = ticker.history(
        period="5d",
        interval="1d",
        auto_adjust=False,
        timeout=15,
        
    )

    if df.empty:
        print("[ECHEC] Aucune donnée reçue")
    else:
        print("[SUCCESS] Yahoo Finance accessible")
        print(f"Nombre de lignes : {len(df)}")
        print(df[["Open", "High", "Low", "Close", "Volume"]].tail())

except Exception as error:
    print("[ECHEC] Yahoo Finance inaccessible")
    print(f"Type : {type(error).__name__}")
    print(f"Détail : {error}")

print("===== FIN DU TEST =====")
