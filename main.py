import asyncio

from apps.web import web_app
import apps.db_migrator as db_migrator
import os
from pathlib import Path

from packages.infra_config import config

if __name__ == '__main__':
    migrations_dir = os.path.join(Path.cwd(), 'alembic')
    db_migrator.run_migrations(config.get_db_dsn(), migrations_dir)
    asyncio.run(web_app.run_task())
