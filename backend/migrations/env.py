import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.core.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.ASYNC_DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import ALL models so their tables are reflected in Base.metadata.
# Without this, autogenerate will not detect new tables and will
# incorrectly try to drop tables it doesn't know about.
from app.models.base import Base
import app.models  # noqa: F401 - ensures all submodules register with Base.metadata

target_metadata = Base.metadata

# Tables that exist in the DB (owned by schema.sql) but are NOT
# managed by SQLAlchemy ORM models. We tell Alembic to ignore
# them during autogenerate so it doesn't emit spurious DROP TABLE.
_SCHEMA_SQL_ONLY_TABLES = {
    "chapters",
    "source_chunks",
    "concept_chunks",
    "generated_questions",
    "graph_versions",
    "graph_validation_results",
    "graph_repair_log",
    "learner_profiles",
    "lesson_sessions",
    "tutor_interactions",
    "assessments",
    "assessment_responses",
    "assessment_outcomes",
    "user_concept_state",
    "concept_mastery",
    "concept_fsrs",
    "fsrs_reviews",
    "mastery_events",
    "content_completions",
    "daily_activity",
    "learning_streaks",
    "book_streaks",
    "progress_snapshots",
    "notifications",
    "curriculum_plans",
}


def include_object(obj, name, type_, reflected, compare_to):
    """
    Exclude tables that are owned by schema.sql (reflected=True, compare_to=None)
    and are not part of our ORM model metadata.
    """
    if type_ == "table" and reflected and compare_to is None:
        return False
    return True

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
