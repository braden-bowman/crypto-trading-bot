import requests
import time
import base64
import ed25519
import pandas as pd
import streamlit as st
from datetime import datetime

# Function to log out
def logout():
    st.session_state.logged_in = False
    st.session_state.account_info = None
    st.session_state.holdings_data = None

# Function to generate signature
def generate_signature(api_key, private_key, path, method, body=""):
    current_timestamp = str(int(time.time()))
    if body:
        message = f"{api_key}{current_timestamp}{path}{method}{body}"
    else:
        message = f"{api_key}{current_timestamp}{path}{method}"
    st.write(f"Message for signature: {message}")
    private_key_bytes = base64.b64decode(private_key)
    st.write(f"Private key bytes: {private_key_bytes}")
    signing_key = ed25519.SigningKey(private_key_bytes[:32])
    signature = signing_key.sign(message.encode("utf-8"))
    base64_signature = base64.b64encode(signature).decode("utf-8")
    st.write(f"Generated signature: {base64_signature}")
    return base64_signature, current_timestamp

# Fetch account information
def fetch_account_info(api_key, private_key):
    path = "/api/v1/crypto/trading/accounts/"
    method = "GET"
    signature, timestamp = generate_signature(api_key, private_key, path, method)
    headers = {
        "x-api-key": api_key,
        "x-signature": signature,
        "x-timestamp": timestamp
    }
    url = "https://trading.robinhood.com" + path
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch account information: {response.text}")
        return None

# Fetch current holdings
def fetch_current_holdings(api_key, private_key):
    path = "/api/v1/crypto/trading/holdings/"
    method = "GET"
    signature, timestamp = generate_signature(api_key, private_key, path, method)
    headers = {
        "x-api-key": api_key,
        "x-signature": signature,
        "x-timestamp": timestamp
    }
    url = "https://trading.robinhood.com" + path
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch current holdings: {response.text}")
        return None

# Fetch historical data for backtesting
def fetch_historical_data(api_key, private_key, symbol: str, interval: str, start: str, end: str) -> pd.DataFrame:
    path = f"/api/v1/marketdata/ohlcv/{symbol}/historical/"
    method = "GET"
    signature, timestamp = generate_signature(api_key, private_key, path, method)
    headers = {
        "x-api-key": api_key,
        "x-signature": signature,
        "x-timestamp": timestamp
    }
    params = {
        "interval": interval,
        "start_time": start,
        "end_time": end
    }
    url = "https://trading.robinhood.com" + path
    st.write(f"URL: {url}")
    st.write(f"Headers: {headers}")
    st.write(f"Params: {params}")
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        return df
    else:
        st.error(f"Failed to fetch historical data: {response.text}")
        return pd.DataFrame()

# Volatility-Based Algorithm for backtesting
def apply_volatility_strategy(df: pd.DataFrame, period: int) -> pd.DataFrame:
    if 'close' not in df.columns:
        st.error("The historical data does not contain 'close' prices.")
        return df
    df['log_return'] = (df['close'] / df['close'].shift(1)).apply(lambda x: pd.np.log(x))
    df['volatility'] = df['log_return'].rolling(window=period).std() * pd.np.sqrt(period)
    df['Signal'] = 0
    df.loc[df['volatility'] > df['volatility'].mean(), 'Signal'] = -1  # Sell signal
    df.loc[df['volatility'] < df['volatility'].mean(), 'Signal'] = 1  # Buy signal
    return df

# Backtest Function
def backtest(api_key, private_key, symbol: str, interval: str, start: str, end: str, period: int, initial_cash: float) -> pd.DataFrame:
    df = fetch_historical_data(api_key, private_key, symbol, interval, start, end)
    if df.empty:
        return df
    df = apply_volatility_strategy(df, period)
    
    if 'Signal' not in df.columns:
        st.error("Failed to apply volatility strategy for backtesting.")
        return pd.DataFrame()
    
    cash = initial_cash
    holdings = 0
    trades = []
    
    for index, row in df.iterrows():
        if row['Signal'] == 1 and cash > 0:
            # Buy
            holdings = cash / row['close']
            cash = 0
            trades.append({"date": index, "type": "buy", "price": row['close'], "holdings": holdings})
        elif row['Signal'] == -1 and holdings > 0:
            # Sell
            cash = holdings * row['close']
            holdings = 0
            trades.append({"date": index, "type": "sell", "price": row['close'], "cash": cash})
    
    # Compute monthly returns
    df['month'] = df.index.to_period('M')
    monthly_returns = []
    for name, group in df.groupby('month'):
        if len(group) > 0:
            start_cash = initial_cash
            end_cash = cash + (holdings * group['close'].iloc[-1])
            monthly_return = (end_cash - start_cash) / start_cash * 100
            monthly_returns.append({"month": name, "return": monthly_return})
            initial_cash = end_cash  # Reset initial_cash for the next month
    
    return pd.DataFrame(monthly_returns)
