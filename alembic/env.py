from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from src.database import Base, engine
from src.models import Users, Books

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()