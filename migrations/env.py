import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Импортируем Base из models.py
from models import Base

# Этот объект конфигурации Alembic, он читает alembic.ini
config = context.config

# Настройка логирования из alembic.ini
fileConfig(config.config_file_name)

# Метаданные вашей ORM (модели).
target_metadata = Base.metadata

# --- Читаем переменные окружения для подключения к БД ---
db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD", "secret")
db_name = os.getenv("DB_NAME", "mydatabase")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")

# Формируем реальный URL
full_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Записываем в объект Alembic
config.set_main_option("sqlalchemy.url", full_url)


def run_migrations_offline():
    """
    Запуск миграций в 'offline' режиме: Alembic генерирует SQL без подключения к БД.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Запуск миграций в 'online' режиме: Alembic реально подключается к БД.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
