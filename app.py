from flask import Flask, render_template, url_for, redirect, request
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from data_fetcher import fetch_all_ticker_data, tickers

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
    mse = mean_squared_error(actual_values, predictions[prediction_intervals[0]])
    mae = mean_absolute_error(actual_values, predictions[prediction_intervals[0]])
    r2 = r2_score(actual_values, predictions[prediction_intervals[0]])
    
    # Generate a plot with the selected ticker data and algorithm predictions
    fig, ax = plt.subplots()
    ax.plot(ticker_times, actual_values, label=f'{selected_ticker} Actual', color='white')
    colors = {
        '1h': 'blue',
        '2h': 'green',
        '6h': 'orange',
        '24h': 'red',
        '3d': 'purple'
    }
    for interval in prediction_intervals:
        ax.plot(ticker_times, predictions[interval], label=f'{interval} Prediction', color=colors[interval])
    
    # Add legend
    ax.legend()
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.title.set_color('white')
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor=fig.get_facecolor())
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close(fig)

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
