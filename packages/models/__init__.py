import enum

import joblib


class Interval(enum.Enum):
    ONE_HOUR = '1h'
    TWO_HOURS = '2h'
    SIX_HOURS = '6h'
    ONE_DAY = '24h'
    THREE_DAYS = '3d'


class Model:
    __period_to_model = {}

    def __init__(self, name: str, source: str):
        self.name = name
        self.source = source

        for interval in Interval:
            self.__period_to_model[interval] = joblib.load(f'{source}_{interval.value}.pkl')

    def predict_interval(self, interval: Interval, ticker_data, actual_values_len):
        x = ticker_data[[f'lag_{lag}' for lag in range(1, 73)]]
        predictions = self.__period_to_model[interval].predict(x)
        min_length = min(len(predictions), actual_values_len)
        return predictions[:min_length]


default_model = Model('LightGBM', 'lightgbm_model')
