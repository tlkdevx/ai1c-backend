from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# импортируем наши настройки и метаданные
from app.core.config import settings
from app.db.base import Base

# this is the Alembic Config object, which provides
# configuration for the migration environment.
config = context.config

# Если вы прописали URL в alembic.ini, можно не вызывать:
# config.set_main_option("sqlalchemy.url", settings.database_url)

# Однако, чтобы брать из .env вместо alembic.ini, раскомментируйте:
config.set_main_option("sqlalchemy.url", str(settings.database_url))


# this line sets up loggers basically.
fileConfig(config.config_file_name)

# Подключаем метаданные вашей модели
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
