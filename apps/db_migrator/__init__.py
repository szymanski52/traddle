from multiprocessing import Process, Queue
from alembic.config import Config
from alembic import command

from apps.background import background_app


def __alembic_upgrade(queue, dsn, script_location):
    try:
        alembic_cfg = Config()
        alembic_cfg.set_main_option('script_location', script_location)
        alembic_cfg.set_main_option('sqlalchemy.url', dsn)
        command.upgrade(alembic_cfg, 'head')
    except Exception as e:
        queue.put(False)
        raise e
    queue.put(True)


def run_migrations(dsn, script_location) -> bool:
    """
    Must run in a subprocess, because otherwise Alembic will mess up logging.
    See: https://stackoverflow.com/questions/24622170/using-alembic-api-from-inside-application-code
    """
    background_app.apply_migrations()

    queue = Queue()
    process = Process(target=__alembic_upgrade, args=(queue, dsn, script_location))
    process.start()
    process.join(timeout=10 * 60)  # 10 min timeout
    return queue.get()
