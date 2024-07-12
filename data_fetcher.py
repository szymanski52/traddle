import yfinance as yf
import pandas as pd
import datetime

tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NFLX", "NVDA", "BABA", "INTC"]

def fetch_ticker_data(ticker):
    df = yf.download(ticker, period="1mo", interval="1h")
    df = df[['Close']]
    df = df.rename(columns={'Close': 'close'})
    
    if 'timestamp' not in df.columns:
        df['timestamp'] = df.index
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    df = df.dropna()
    
    print(f"Fetched data for {ticker}:")
    print(df.head())
    
    return df

def fetch_all_ticker_data():
    ticker_data = {ticker: fetch_ticker_data(ticker) for ticker in tickers}
    return ticker_data
