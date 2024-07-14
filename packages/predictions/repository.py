from sqlalchemy import create_engine, select, and_, func, column
from sqlalchemy.orm import Session

from packages.predictions import ModelMetrics
from packages.predictions.persistance import Base

postgresql_engine = None


def init(uri):
    global postgresql_engine
    postgresql_engine = create_engine(uri, echo=False)
    Base.metadata.create_all(postgresql_engine)
    Base.metadata.bind = postgresql_engine


def save_metrics(metrics: ModelMetrics):
    with Session(postgresql_engine) as session:
        session.add(metrics)
        session.commit()


def get_metrics_aggregated_by_mean(ticker_symbol: str, interval: str):
    with (Session(postgresql_engine) as session):
        last_five = select(
            ModelMetrics.model_key.label("model_key"),
            ModelMetrics.mse.label("mse"),
            ModelMetrics.mae.label("mae"),
            ModelMetrics.r2.label("r2")
        ).where(
            and_(ModelMetrics.interval == interval,
                 ModelMetrics.ticker_symbol == ticker_symbol)
        ).order_by(ModelMetrics.timestamp.desc()).limit(5).cte("last_five")

        statement = select(
            column('model_key'),
            func.avg(column('mse')).label("avg_mse"),
            func.avg(column('mae')).label("avg_mae"),
            func.avg(column('r2')).label("avg_r2")
        ).select_from(last_five).group_by('model_key')

        result = session.execute(statement).all()
        # noinspection PyProtectedMember
        return [row._asdict() for row in result]
