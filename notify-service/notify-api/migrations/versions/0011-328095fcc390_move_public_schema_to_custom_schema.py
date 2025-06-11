"""move public schema to custom schema

Revision ID: 328095fcc390
Revises: d6a8ffda6b9c
Create Date: 2025-06-10 14:39:17.930581

"""
import logging
import os
import re
from pathlib import Path

import sqlalchemy as sa
from alembic import op
from alembic.script import ScriptDirectory
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '328095fcc390'
down_revision = 'd6a8ffda6b9c'
branch_labels = None
depends_on = None

logger = logging.getLogger(__name__)


def validate_schema_name(schema):
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', schema):
        raise ValueError(f"Invalid schema name: {schema}")


def get_target_schema():
    # Import Config class directly since it's already available in the env.py
    from notify_api.config import Config

    # Get schema from environment or config
    schema = os.getenv("NOTIFY_DATABASE_SCHEMA", Config.DB_SCHEMA)
    validate_schema_name(schema)
    return schema


def get_previous_migrations():
    # Get the directory containing the migrations
    migrations_dir = Path(__file__).parent.parent
    script = ScriptDirectory(str(migrations_dir))
    
    # Get all revisions up to and including the down_revision
    revisions = []
    current = script.get_revision(down_revision)
    while current:
        revisions.append(current)
        for parent in current.nextrev:
            current = script.get_revision(parent)
            break
        else:
            current = None
    return reversed(revisions)


def schema_exists(conn, schema):
    if schema == 'public':  # Always exists
        return True
    result = conn.execute(
        text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :schema"),
        {'schema': schema}
    )
    return result.scalar() == 1


def apply_migration_in_schema(migration, schema):
    conn = op.get_bind()
    trans = conn.begin()
    
    try:
        # Save original search path
        result = conn.execute(text('SHOW search_path'))
        original_search_path = result.scalar()
        
        try:
            # Set search path to only your target schema
            conn.execute(text(f'SET search_path TO {schema}'))
            logger.info(f"Applying migration {migration.revision} in schema {schema}")
            migration.module.upgrade()
        finally:
            # Always restore the original search path
            conn.execute(text(f"SET search_path TO {original_search_path}"))
        
        trans.commit()
    except Exception as e:
        trans.rollback()
        logger.error(f"Failed to apply migration {migration.revision}: {str(e)}")
        raise


def revert_migration_in_schema(migration, schema):
    conn = op.get_bind()
    trans = conn.begin()
    
    try:
        # Save original search path
        result = conn.execute(text('SHOW search_path'))
        original_search_path = result.scalar()
        
        try:
            # Set search path to our schema
            conn.execute(text(f'SET search_path TO {schema}'))
            logger.info(f"Reverting migration {migration.revision} in schema {schema}")
            migration.module.downgrade()
        finally:
            # Always restore the original search path
            conn.execute(text(f"SET search_path TO {original_search_path}"))
        
        trans.commit()
    except Exception as e:
        trans.rollback()
        logger.error(f"Failed to revert migration {migration.revision}: {str(e)}")
        raise


def upgrade():
    target_schema = get_target_schema()
    
    # Skip if target schema is public
    if target_schema == 'public':
        logger.info("Target schema is public, skipping migration")
        return
    
    conn = op.get_bind()
    if not schema_exists(conn, target_schema):
        logger.info(f"Creating schema {target_schema}")
        op.execute(f"CREATE SCHEMA {target_schema}")
    
    # Get all previous migrations
    migrations = get_previous_migrations()
    
    # Apply each migration in the new schema
    for migration in migrations:
        apply_migration_in_schema(migration, target_schema)


def downgrade():
    target_schema = get_target_schema()
    
    # Skip if target schema is public
    if target_schema == 'public':
        logger.info("Target schema is public, skipping downgrade")
        return
    
    conn = op.get_bind()
    if not schema_exists(conn, target_schema):
        logger.info(f"Schema {target_schema} does not exist, nothing to downgrade")
        return
    
    # Get all previous migrations in reverse order
    migrations = list(get_previous_migrations())
    
    # Revert each migration in the new schema
    for migration in reversed(migrations):
        revert_migration_in_schema(migration, target_schema)
    
    # Optionally drop the schema (commented out for safety)
    # logger.info(f"Dropping schema {target_schema}")
    # op.execute(f"DROP SCHEMA IF EXISTS {target_schema}")