
#!/bin/bash
set -euo pipefail

cd "$HOME/Desktop/portfolio_boursier"

echo "===== DEBUT ACTUALISATION ====="
date

make update

echo "===== FIN ACTUALISATION ====="
date
