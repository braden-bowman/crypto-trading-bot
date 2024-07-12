import cryptocompare
import yfinance as yf
from binance.client import Client
import pandas as pd
from datetime import datetime, timedelta
import os
import time

def download_crypto_data(symbol, binance_symbol, start_date, end_date, interval, file_name):
    data = None

    # Try downloading from CryptoCompare
    try:
        print(f"Trying to download data from CryptoCompare for {symbol}...")
        all_data = []
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        while start_dt < end_dt:
            next_end_dt = min(start_dt + timedelta(days=60), end_dt)
            data = cryptocompare.get_historical_price_minute(symbol, currency='USD', limit=2000, toTs=int(next_end_dt.timestamp()))
            if data:
                all_data.extend(data)
            start_dt = next_end_dt
            time.sleep(1)  # Sleep to avoid rate limit issues
        if all_data:
            data = pd.DataFrame(all_data)
            data['time'] = pd.to_datetime(data['time'], unit='s')
            data.set_index('time', inplace=True)
        print("Data downloaded from CryptoCompare.")
    except Exception as e:
        print(f"Failed to download data from CryptoCompare: {e}")

    # If CryptoCompare fails, try yfinance
    if data is None or data.empty:
        try:
            print(f"Trying to download data from Yahoo Finance for {symbol}...")
            yf_data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
            if not yf_data.empty:FileNotFoundError: [Errno 2] No such file or directory: 'download_crypto_data.py'

                yf_data.index = pd.to_datetime(yf_data.index)
                data = yf_data
            print("Data downloaded from Yahoo Finance.")
        except Exception as e:
            print(f"Failed to download data from Yahoo Finance: {e}")

    # If yfinance fails, fallback to Binance
    if data is None or data.empty:
        try:
            print(f"Trying to download data from Binance for {binance_symbol}...")
            client = Client()
            all_data = []
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            while start_dt < end_dt:
                next_end_dt = min(start_dt + timedelta(days=60), end_dt)
                klines = client.get_historical_klines(binance_symbol, interval, start_dt.strftime("%d %b, %Y"), next_end_dt.strftime("%d %b, %Y"))
                if klines:
                    for kline in klines:
                        all_data.append({
                            'time': datetime.fromtimestamp(kline[0] / 1000),
                            'open': float(kline[1]),
                            'high': float(kline[2]),
                            'low': float(kline[3]),
                            'close': float(kline[4]),
                            'volume': float(kline[5])
                        })
                start_dt = next_end_dt
                time.sleep(1)  # Sleep to avoid rate limit issues
            if all_data:
                data = pd.DataFrame(all_data)
                data.set_index('time', inplace=True)
            print("Data downloaded from Binance.")
        except Exception as e:
            print(f"Failed to download data from Binance: {e}")

    if data is not None and not data.empty:
        data.to_csv(file_name)
        print(f"Data downloaded and saved to {file_name}")
    else:
        print("Failed to download data from all sources.")

if __name__ == "__main__":
    # Define parameters
    crypto_symbol = 'BTC-USD'  # Use Yahoo Finance format
    binance_symbol = 'BTCUSDT'  # Use Binance format
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')  # Start date within last 7 days for yfinance
    end_date = datetime.now().strftime('%Y-%m-%d')
    interval = '1m'  # 1-minute interval
    output_file = 'crypto_data.csv'
    
    # Download and save the data
    download_crypto_data(crypto_symbol, binance_symbol, start_date, end_date, interval, output_file)
    print(f"Data downloaded and saved to {output_file}")
