#!/bin/sh

# Apply database migrations
/app/.venv/bin/alembic upgrade head

# Start the FastAPI application
/app/.venv/bin/fastapi run fastapi_2fa_example/main.py --host 0.0.0.0 --port 8000
