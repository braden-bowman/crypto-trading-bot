import requests
import pandas as pd
import numpy as np
import time

# Constants
API_URL = "https://api.your-crypto-data-source.com/v1/ohlcv"  # Replace with your data source API
SYMBOL = "ETH-USD"
INTERVAL = "5m"  # 5-minute intervals
PERIOD = 20  # Period for SMA and standard deviation
TRADE_AMOUNT = 1  # Amount in USD to trade

def fetch_historical_data(symbol, interval, limit=100):
    """Fetch historical data for the given symbol and interval."""
    url = f"{API_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)
    return df

def compute_bollinger_bands(df, period):
    """Compute Bollinger Bands."""
    df['SMA'] = df['close'].rolling(window=period).mean()
    df['STD'] = df['close'].rolling(window=period).std()
    df['Upper Band'] = df['SMA'] + (df['STD'] * 2)
    df['Lower Band'] = df['SMA'] - (df['STD'] * 2)
    return df

def generate_signals(df):
    """Generate buy and sell signals based on Bollinger Bands."""
    df['Signal'] = 0
    df['Signal'][df['close'] < df['Lower Band']] = 1  # Buy signal
    df['Signal'][df['close'] > df['Upper Band']] = -1  # Sell signal
    return df

def main():
    """Main function to run the trading algorithm."""
    while True:
        # Check the state from the Streamlit app
        response = requests.get("http://localhost:8501/get_run_state")
        state = response.json().get("run", False)

        if state:
            df = fetch_historical_data(SYMBOL, INTERVAL)
            df = compute_bollinger_bands(df, PERIOD)
            df = generate_signals(df)

            last_signal = df['Signal'].iloc[-1]
            if last_signal == 1:
                print("Buy signal generated. Executing buy trade...")
                # Call your trade execution function here
                # execute_trade("buy", TRADE_AMOUNT)
            elif last_signal == -1:
                print("Sell signal generated. Executing sell trade...")
                # Call your trade execution function here
                # execute_trade("sell", TRADE_AMOUNT)

        time.sleep(1800)  # Wait for 30 minutes before checking again

if __name__ == "__main__":
    main()
