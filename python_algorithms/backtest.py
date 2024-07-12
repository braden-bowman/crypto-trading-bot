import streamlit as st
import requests
import subprocess
import pandas as pd
import time
import base64
import ed25519
from streamlit_js_eval import streamlit_js_eval
import json

# Initialize session state for viewport width
if "viewport_width" not in st.session_state:
    st.session_state["viewport_width"] = streamlit_js_eval(js_expressions="window.innerWidth", key="ViewportWidth")

viewport_width = st.session_state["viewport_width"]

# Calculate column widths based on viewport width
col1_width = viewport_width * 0.25 if viewport_width else 300
col2_width = viewport_width * 0.50 if viewport_width else 600
col3_width = viewport_width * 0.25 if viewport_width else 300

# Function to log out
def logout():
    st.session_state.logged_in = False
    st.session_state.account_info = None
    st.session_state.holdings_data = None

# Function to generate signature
def generate_signature(api_key, private_key, path, method, body=""):
    current_timestamp = str(int(time.time()))
    message = f"{api_key}{current_timestamp}{path}{method}{body}"
    private_key_bytes = base64.b64decode(private_key)
    signing_key = ed25519.SigningKey(private_key_bytes)
    signature = signing_key.sign(message.encode("utf-8"))
    base64_signature = base64.b64encode(signature).decode("utf-8")
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
def fetch_historical_data(symbol: str, interval: str, start: str, end: str) -> pd.DataFrame:
    path = f"/api/v1/marketdata/ohlcv/{symbol}/historical/"
    method = "GET"
    params = {
        "interval": interval,
        "start_time": start,
        "end_time": end
    }
    url = "https://trading.robinhood.com" + path
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)
    else:
        st.error(f"Failed to fetch historical data: {response.text}")
        return pd.DataFrame()

# Bollinger Bands Algorithm for backtesting
def apply_bollinger_bands(df: pd.DataFrame, period: int) -> pd.DataFrame:
    df['SMA'] = df['close'].rolling(window=period).mean()
    df['STD'] = df['close'].rolling(window=period).std()
    df['Upper Band'] = df['SMA'] + (df['STD'] * 2)
    df['Lower Band'] = df['SMA'] - (df['STD'] * 2)
    df['Signal'] = 0
    df['Signal'][df['close'] < df['Lower Band']] = 1  # Buy signal
    df['Signal'][df['close'] > df['Upper Band']] = -1  # Sell signal
    return df

# Backtest Function
def backtest(symbol: str, interval: str, start: str, end: str, period: int, initial_cash: float) -> pd.DataFrame:
    df = fetch_historical_data(symbol, interval, start, end)
    df = apply_bollinger_bands(df, period)
    
    cash = initial_cash
    holdings = 0
    trades = []
    
    for index, row in df.iterrows():
        if row['Signal'] == 1 and cash > 0:
