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

# Load the trained model
model = joblib.load('lightgbm_model.pkl')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/algorithms')
def show_algorithms():
    return render_template('algorithms.html', algorithms=algorithms)

@app.route('/algorithm/<name>', methods=['GET', 'POST'])
def show_algorithm(name):
    selected_ticker = request.form.get('ticker', tickers[0])
    
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

    X_pred = pd.DataFrame({
        'hour': ticker_data_pred.index.hour,
        'day': ticker_data_pred.index.day,
        'month': ticker_data_pred.index.month
    })
    
    # Generate predictions with the model
    predictions = model.predict(X_pred)
    
    # Ensure matching lengths of predictions and actual values
    min_length = min(len(predictions), len(actual_values))
    predictions = predictions[:min_length]
    actual_values = actual_values[:min_length]
    ticker_times = ticker_times[:min_length]
    
    # Calculate metrics
    mse = mean_squared_error(actual_values, predictions)
    mae = mean_absolute_error(actual_values, predictions)
    r2 = r2_score(actual_values, predictions)
    
    # Generate a plot with the selected ticker data and algorithm predictions
    fig, ax = plt.subplots()
    ax.plot(ticker_times, predictions, label='Algorithm Prediction')
    ax.plot(ticker_times, actual_values, label=selected_ticker)
    
    # Add legend
    ax.legend()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
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
        r2=r2
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
