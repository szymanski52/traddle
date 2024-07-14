import datetime

from packages.predictions.metrics import ModelMetrics
from packages.predictions.models import default_model, Interval
from packages.predictions.tickers import all_tickers_data, Ticker


def predict_basic(selected_ticker: str, prediction_intervals: list):
    pred_start_date = datetime.datetime(2024, 7, 7, tzinfo=datetime.timezone.utc)
    pred_end_date = datetime.datetime(2024, 7, 9, tzinfo=datetime.timezone.utc)
    test_start_date = datetime.datetime(2024, 7, 10, tzinfo=datetime.timezone.utc)
    test_end_date = datetime.datetime(2024, 7, 12, tzinfo=datetime.timezone.utc)

    ticker_data_pred = all_tickers_data[selected_ticker].loc[
        (all_tickers_data[selected_ticker].index >= pred_start_date) & (
                all_tickers_data[selected_ticker].index <= pred_end_date)]

    ticker_data_test = all_tickers_data[selected_ticker].loc[
        (all_tickers_data[selected_ticker].index >= test_start_date) & (
                all_tickers_data[selected_ticker].index <= test_end_date)]

    ticker_times = ticker_data_test.index
    actual_values = ticker_data_test['close'].values

    if len(ticker_data_pred) == 0 or len(ticker_data_test) == 0:
        return f"Not enough data for the selected period for ticker {selected_ticker}.", 400

    max_len = len(actual_values)

    predictions = {}
    min_length = max_len
    for interval in prediction_intervals:
        predictions[interval] = default_model.predict_interval(interval, ticker_data_pred, max_len)
        min_length = min(len(predictions[interval]), max_len)

    actual_values = actual_values[:min_length]
    ticker_times = ticker_times[:min_length]

    return ticker_times, actual_values, predictions


def get_metrics(actual_values, predictions, ticker: Ticker):
    model_metrics = ModelMetrics(default_model, ticker, Interval.ONE_HOUR)
    model_metrics.calculate(actual_values, predictions)

    return model_metrics