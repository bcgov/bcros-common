#!/bin/bash

set -e

# Simple configuration - edit these values directly when needed
ACTION="upgrade"
SCHEMA="public" 
ARGS="head"

# Set environment variables
export NOTIFY_DATABASE_SCHEMA=$SCHEMA

# Start services if not running
docker compose up -d postgres

# Wait for postgres to be ready
echo "Waiting for Postgres to be ready..."
docker compose exec postgres sh -c "until pg_isready -U notifyuser; do sleep 2; done;"
echo "Postgres is ready!"

# Run migrations using alembic directly instead of flask db
# docker compose run --rm migration alembic $ACTION $ARGS

# echo "Migration complete!"
