from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from packages.predictions.models import Model, Interval
from packages.predictions.tickers import Ticker


class ModelMetrics:
    def __init__(self, model: Model, ticker: Ticker, interval: Interval):
        self.model_key = model.key
        self.ticker_symbol = ticker.symbol
        self.interval = interval

        self.mse = None
        self.mae = None
        self.r2 = None

    def calculate(self, actual_values, predictions):
        self.mse = mean_squared_error(actual_values, predictions)
        self.mae = mean_absolute_error(actual_values, predictions)
        self.r2 = r2_score(actual_values, predictions)
