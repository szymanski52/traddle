import asyncio
import sys

from apps.background import background_app
from apps.web import web_app
import apps.db_migrator as db_migrator
import os
from pathlib import Path

from packages.infra_config import config

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == '__main__':
    migrations_dir = os.path.join(Path.cwd(), 'alembic')
    db_migrator.run_migrations(config.get_db_dsn(), migrations_dir)


    @web_app.before_serving
    async def before_web_app_serving():
        web_app.add_background_task(background_app.start)


    asyncio.run(web_app.run_task())
