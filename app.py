from flask import Flask, render_template, url_for, redirect, request
import datetime
import joblib
from data_fetcher import fetch_all_ticker_data, tickers
from algorithm import calculate_metrics, plot_predictions

app = Flask(__name__)

# Demo account balance
balance = 1000

# List of trading algorithms
algorithms = ["Algorithm 1", "Algorithm 2", "Algorithm 3"]

# Fetch data for all tickers
ticker_data = fetch_all_ticker_data()

# Convert all indices to UTC if not already in UTC
for ticker in tickers:
    if ticker_data[ticker].index.tz is None:
        ticker_data[ticker].index = ticker_data[ticker].index.tz_localize('UTC')
    else:
        ticker_data[ticker].index = ticker_data[ticker].index.tz_convert('UTC')

# Create lag features for the past 3 days (72 hours)
for ticker in tickers:
    for lag in range(1, 73):
        ticker_data[ticker][f'lag_{lag}'] = ticker_data[ticker]['close'].shift(lag)
    ticker_data[ticker] = ticker_data[ticker].dropna()

# Load the trained models
models = {
    '1h': joblib.load('lightgbm_model_1h.pkl'),
    '2h': joblib.load('lightgbm_model_2h.pkl'),
    '6h': joblib.load('lightgbm_model_6h.pkl'),
    '24h': joblib.load('lightgbm_model_24h.pkl'),
    '3d': joblib.load('lightgbm_model_3d.pkl')
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/algorithms')
def show_algorithms():
    return render_template('algorithms.html', algorithms=algorithms)

@app.route('/algorithm/<name>', methods=['GET', 'POST'])
def show_algorithm(name):
    selected_ticker = request.form.get('ticker', tickers[0])
    prediction_intervals = request.form.getlist('intervals')
    
    if not prediction_intervals:
        prediction_intervals = ['1h', '2h', '6h', '24h', '3d']

    # Define prediction and input periods
    pred_start_date = datetime.datetime(2024, 7, 7, tzinfo=datetime.timezone.utc)
    pred_end_date = datetime.datetime(2024, 7, 9, tzinfo=datetime.timezone.utc)
    test_start_date = datetime.datetime(2024, 7, 10, tzinfo=datetime.timezone.utc)
    test_end_date = datetime.datetime(2024, 7, 12, tzinfo=datetime.timezone.utc)
    
    ticker_data_pred = ticker_data[selected_ticker].loc[(ticker_data[selected_ticker].index >= pred_start_date) & (ticker_data[selected_ticker].index <= pred_end_date)]
    ticker_data_test = ticker_data[selected_ticker].loc[(ticker_data[selected_ticker].index >= test_start_date) & (ticker_data[selected_ticker].index <= test_end_date)]
    
    ticker_times = ticker_data_test.index
    actual_values = ticker_data_test['close'].values
    
    if len(ticker_data_pred) == 0 or len(ticker_data_test) == 0:
        return f"Not enough data for the selected period for ticker {selected_ticker}.", 400

    X_pred = ticker_data_pred[[f'lag_{lag}' for lag in range(1, 73)]]
    
    predictions = {}
    for interval in prediction_intervals:
        preds = models[interval].predict(X_pred)
        min_length = min(len(preds), len(actual_values))
        predictions[interval] = preds[:min_length]

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
        tickers=tickers,
        selected_ticker=selected_ticker,
        ticker_data=ticker_data[selected_ticker],
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
