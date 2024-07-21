import procrastinate

from packages.predictions import predict_everything


async def start(dsn):
    app = procrastinate.App(connector=procrastinate.PsycopgConnector(conninfo=dsn))

    @app.task()
    async def predict():
        predict_everything()

    app.periodic(
        cron='0 * * * *',
        queue='default',
    )(predict)

    await app.run_worker_async()
