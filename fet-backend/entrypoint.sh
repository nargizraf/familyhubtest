#!/bin/sh
set -eu

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

python - <<'PY'
import sys
import time

from sqlalchemy import create_engine, text

from app.config import settings

for attempt in range(30):
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001 - retry until Postgres accepts connections
        print(f"Waiting for database ({attempt + 1}/30): {exc}", flush=True)
        time.sleep(2)

print("Database did not become ready in time.", flush=True)
sys.exit(1)
PY

alembic upgrade head
python -m app.seed
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
