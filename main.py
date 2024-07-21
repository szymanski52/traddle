from apps.web import web_app
import apps.db_migrator as db_migrator
import os
from pathlib import Path

from packages.infra_config import config

migrations_dir = os.path.join(Path.cwd(), 'alembic')
db_migrator.run_migrations(config.get_db_dsn(), migrations_dir)

web_app.run_task()
