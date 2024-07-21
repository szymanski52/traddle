from apps.web import web_app
import apps.db_migrator as db_migrator
import os
from pathlib import Path

db_dsn = 'postgresql://postgres:postgres@localhost:8432/traddle'

migrations_dir = os.path.join(Path.cwd(), 'alembic')
db_migrator.run_migrations(db_dsn, migrations_dir)
web_app.run_task()
