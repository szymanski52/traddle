import procrastinate
from procrastinate.exceptions import ConnectorException

from packages.infra_config import config
from packages.predictions import predict_everything

__procrastinate_app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(
        conninfo=config.get_db_dsn()
    )
)


class BackgroundApp:
    def __init__(self):
        self.__procrastinate_app = procrastinate.App(
            connector=procrastinate.PsycopgConnector(
                conninfo=config.get_db_dsn()
            )
        )

    def apply_migrations(self):
        with self.__procrastinate_app.open():
            try:
                self.__procrastinate_app.schema_manager.apply_schema()
            except ConnectorException as e:
                pass

    async def start(self):
        @self.__procrastinate_app.task()
        async def predict(timestamp):
            predict_everything()

        async with self.__procrastinate_app.open_async():
            self.__procrastinate_app.periodic(
                cron='*/1 * * * *',
                queue='default',
            )(predict)
            await self.__procrastinate_app.run_worker_async(install_signal_handlers=False)


background_app = BackgroundApp()
