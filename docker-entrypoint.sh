#!/bin/bash
set -e

# Run database initialization/migrations
echo "Running database initialization..."
python init_prod_db.py

# Execute the main command (gunicorn)
exec "$@"
