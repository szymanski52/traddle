import uuid
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sqlalchemy import String, Column, DateTime, func, types
from sqlalchemy.orm import Mapped, mapped_column

from packages.predictions.models import Model, Interval
from packages.predictions.persistance import Base
from packages.predictions.tickers import Ticker


class ModelMetrics(Base):
    __tablename__ = 'model_metrics'

    id: Mapped[UUID] = mapped_column(types.UUID, primary_key=True)
    model_key: Mapped[UUID]
    ticker_symbol: Mapped[str] = mapped_column(String(5))
    interval: Mapped[str] = mapped_column(String(3))
    mse: Mapped[Optional[float]]
    mae: Mapped[Optional[float]]
    r2: Mapped[Optional[float]]
    timestamp = Column(DateTime, default=func.now())

    def __init__(self, model: Model, ticker: Ticker, interval: Interval, **kw: Any):
        super().__init__(**kw)
        self.model_key = model.key
        self.ticker_symbol = ticker.symbol
        self.interval = interval.value
        self.id = uuid.uuid4()

        self.mse = None
        self.mae = None
        self.r2 = None

    def calculate(self, actual_values, predictions):
        self.timestamp = datetime.utcnow()
        self.mse = mean_squared_error(actual_values, predictions)
        self.mae = mean_absolute_error(actual_values, predictions)
        self.r2 = r2_score(actual_values, predictions)
