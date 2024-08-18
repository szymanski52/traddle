import yfinance as yf
import pandas as pd


class Ticker:
    def __init__(self, symbol: str, name: str):
        self.symbol = symbol
        self.name = name

    def get_data(self, period="1mo", interval="1h"):
        df = yf.download(self.symbol, period=period, interval=interval)
        df = df[['Close']]
        df = df.rename(columns={'Close': 'close'})

        if 'timestamp' not in df.columns:
            df['timestamp'] = df.index

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        df = df.dropna()

        df = Ticker.__fix_tz(df)
        #df = Ticker.__create_lag_features(df)

        return df

    @staticmethod
    def __fix_tz(df):
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        else:
            df.index = df.index.tz_convert('UTC')
        return df

    @staticmethod
    def __create_lag_features(df):
        for lag in range(1, 73):
            df[f'lag_{lag}'] = df['close'].shift(lag)
        return df


all_tickers = [
    Ticker("AAPL", "Apple Inc."),
    Ticker("GOOGL", "Alphabet Inc."),
    Ticker("MSFT", "Microsoft Corporation"),
    Ticker("AMZN", "Amazon.com Inc."),
    Ticker("TSLA", "Tesla Inc."),
    Ticker("META", "Meta Platforms Inc."),
    Ticker("NFLX", "Netflix Inc."),
    Ticker("NVDA", "NVIDIA Corporation"),
    Ticker("BABA", "Alibaba Group Holding Limited"),
    Ticker("INTC", "Intel Corporation")
]

all_tickers_data = {ticker.symbol: ticker.get_data() for ticker in all_tickers}
