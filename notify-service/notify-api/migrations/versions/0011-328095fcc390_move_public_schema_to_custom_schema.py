"""move public schema to custom schema

Revision ID: 328095fcc390
Revises: d6a8ffda6b9c
Create Date: 2025-06-10 14:39:17.930581

"""
import importlib.util
import logging
import os
import re
from pathlib import Path

from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '328095fcc390'
down_revision = 'd6a8ffda6b9c'
branch_labels = None
depends_on = None

logger = logging.getLogger(__name__)

def get_target_schema():
    """Minimal schema name fetch with validation."""
    schema = os.getenv("NOTIFY_DATABASE_SCHEMA", "public")
    if not re.match(r'^[a-z_][a-z0-9_]*$', schema, re.I):
        raise ValueError(f"Invalid schema name: {schema}")
    return schema

def get_migration_files():
    """Get sorted migration files."""
    migrations_dir = Path(__file__).parent.parent / 'versions'
    return sorted(
        f for f in os.listdir(migrations_dir)
        if f.endswith('.py') and f != '__init__.py'
    )

def load_migration_module(file_path):
    """Load a migration module from file."""
    spec = importlib.util.spec_from_file_location(f"migration_{file_path.stem}", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def upgrade():
    target_schema = get_target_schema()
    if target_schema == 'public':
        logger.info("Target schema is public, skipping migration")
        return
    
    conn = op.get_bind()
    
    # Save original search path
    result = conn.execute(text('SHOW search_path'))
    original_search_path = result.scalar()
    logger.info(f"Original search path: {original_search_path}")
    
    # Create schema if it doesn't exist
    if not conn.execute(
        text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :schema"),
        {'schema': target_schema}
    ).scalar():
        conn.execute(text(f"CREATE SCHEMA {target_schema}"))

    try:
        # Set search path to ONLY the target schema
        conn.execute(text(f"SET search_path TO {target_schema}"))
        logger.info(f"Set search path to {target_schema} only")

        migrations_dir = Path(__file__).parent.parent / 'versions'
        for file in get_migration_files():
            if file == os.path.basename(__file__):
                logger.info(f"Skipping current migration file {file}")
                continue

            file_path = migrations_dir / file
            try:
                module = load_migration_module(file_path)
                logger.info(f"Applying {file} in schema {target_schema}")
                module.upgrade()
                logger.info(f"Successfully applied {file}")
            except Exception as e:
                logger.error(f"Failed to apply {file}: {str(e)}")
                raise

        # Set the search path for the database after successful migration
        logger.info(f"Setting database search_path to include {target_schema}")
        conn.execute(text(f"""
            ALTER DATABASE {conn.engine.url.database}
            SET search_path TO {target_schema}, public
        """))

    finally:
        # Always restore original search path for the connection
        conn.execute(text(f"SET search_path TO {original_search_path}"))
        logger.info(f"Restored connection search path to {original_search_path}")

def downgrade():
    target_schema = get_target_schema()
    
    # Skip if target schema is public
    if target_schema == 'public':
        logger.info("Target schema is public, skipping downgrade")
        return
    
    conn = op.get_bind()

    # Check if schema exists
    if not conn.execute(
        text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :schema"),
        {'schema': target_schema}
    ).scalar():
        logger.info(f"Schema {target_schema} does not exist, nothing to downgrade")
        return
    
    # Drop the schema with all its contents
    conn.execute(text(f"DROP SCHEMA {target_schema} CASCADE"))
    logger.info(f"Dropped schema {target_schema}")
    
    # Reset database search path to default
    conn.execute(text(f"""
        ALTER DATABASE {conn.engine.url.database}
        SET search_path TO "$user", public
    """))
    logger.info("Reset database search path to default")