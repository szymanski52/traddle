from flask import Flask, render_template, url_for, redirect, request
import datetime

from packages.models import Interval, default_model
from packages.tickers import all_tickers_data, all_tickers

app = Flask(__name__)

# Demo account balance
balance = 1000

# List of trading algorithms
algorithms = ["Algorithm 1", "Algorithm 2", "Algorithm 3"]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/algorithms')
def show_algorithms():
    return render_template('algorithms.html', algorithms=algorithms)


@app.route('/algorithm/<name>', methods=['GET', 'POST'])
def show_algorithm(name):
    selected_ticker = request.form.get('ticker', default=all_tickers[0].symbol)
    prediction_intervals = request.form.getlist('intervals')

    if not prediction_intervals:
        prediction_intervals = [e for e in Interval]

    # Define prediction and input periods
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

    # Calculate metrics for the first interval (to show in the template)
    mse, mae, r2 = calculate_metrics(actual_values, predictions[prediction_intervals[0]])

    # Generate a plot with the selected ticker data and algorithm predictions
    plot_url = plot_predictions(ticker_times, actual_values, predictions, prediction_intervals)

    return render_template(
        'algorithm.html',
        name=name,
        plot_url=plot_url,
        tickers=all_tickers,
        selected_ticker=selected_ticker,
        ticker_data=all_tickers_data[selected_ticker],
        mse=mse,
        mae=mae,
        r2=r2,
        prediction_intervals=prediction_intervals
    )


@app.route('/dashboard')
def dashboard():
    global balance
    return render_template('dashboard.html', balance=balance)


@app.route('/top_up')
def top_up():
    global balance
    balance += 100
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
