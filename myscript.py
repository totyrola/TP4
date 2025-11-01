import os
import sys

BAD = os.environ.get("BAD_HASH", "c1a4be04b972b6c17db242fc37752ad517c29402")
GOOD = os.environ.get("GOOD_HASH", "e4cfc6f77ebbe2e23550ddab682316ab4ce1c03c")

def run(cmd):
    print(f"+ {cmd}", flush=True)
    return os.system(cmd)

# Sécurité GitHub Actions (pas bloqué par safe.directory) — non fatal si ça échoue
run("git config --global --add safe.directory $(pwd) || true")

# Toujours repartir propre
run("git bisect reset || true")

# Démarrer le bisect (ordre : bad puis good)
rc = run(f"git bisect start {BAD} {GOOD}")
if rc != 0:
    sys.exit(rc)

# Commande exécutée à CHAQUE commit durant le bisect :
# - installe deps si présents
# - si Django: migrate + tests; sinon: pytest
test_cmd = (
    'bash -lc "'
    'python -m pip install -r requirements.txt >/dev/null 2>&1 || true; '
    'if [ -f manage.py ]; then '
    '  python manage.py migrate --noinput >/dev/null 2>&1 || true; '
    '  python manage.py test -v 2; '
    'else '
    '  python -m pip install pytest >/dev/null 2>&1 || true; '
    '  pytest -q; '
    'fi"'
)

rc = run(f"git bisect run {test_cmd}")

# On revient à l’état initial pour laisser le runner propre
run("git bisect reset")

# Propager le statut
sys.exit(0 if rc == 0 else 1)
