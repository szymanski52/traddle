from quart import Quart, render_template, url_for, redirect, request

from algorithm import plot_predictions
from packages.predictions import predict_basic, get_metrics, repository
from packages.predictions.models import Interval
from packages.predictions.tickers import all_tickers_data, all_tickers

web_app = Quart(__name__)

# Demo account balance
balance = 1000

# List of trading algorithms
algorithms = ["Algorithm 1", "Algorithm 2", "Algorithm 3"]

repository.init('postgresql://postgres:postgres@localhost:8432/traddle')


@web_app.route('/')
async def index():
    return await render_template('index.html')


@web_app.route('/algorithms')
async def show_algorithms():
    return await render_template('algorithms.html', algorithms=algorithms)


@web_app.route('/algorithm/<name>', methods=['GET', 'POST'])
async def show_algorithm(name):
    form = await request.form
    request_ticker = form.get('ticker', default=all_tickers[0].symbol)
    ticker = [ticker for ticker in all_tickers if ticker.symbol == request_ticker][0]
    prediction_intervals = form.getlist('intervals')

    if not prediction_intervals:
        prediction_intervals = [e for e in Interval]

    ticker_times, actual_values, predictions = predict_basic(ticker.symbol, prediction_intervals)

    metrics = get_metrics(actual_values, predictions[prediction_intervals[0]], ticker)

    # Generate a plot with the selected ticker data and algorithm predictions
    plot_url = plot_predictions(ticker_times, actual_values, predictions, prediction_intervals)

    return await render_template(
        'algorithm.html',
        name=name,
        plot_url=plot_url,
        tickers=all_tickers,
        selected_ticker=ticker.symbol,
        ticker_data=all_tickers_data[ticker.symbol],
        mse=metrics.mse,
        mae=metrics.mae,
        r2=metrics.r2,
        prediction_intervals=prediction_intervals
    )


@web_app.route('/dashboard')
async def dashboard():
    global balance
    return await render_template('dashboard.html', balance=balance)


@web_app.route('/top_up')
async def top_up():
    global balance
    balance += 100
    return redirect(url_for('dashboard'))
