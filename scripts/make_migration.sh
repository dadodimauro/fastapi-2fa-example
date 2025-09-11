# !/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <migration message>"
  exit 1
fi

POSTGRES_HOST=localhost alembic revision --autogenerate -m "$1"