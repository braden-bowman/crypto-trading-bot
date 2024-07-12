import streamlit as st
import subprocess
import pandas as pd
from streamlit_js_eval import streamlit_js_eval
from utils import (
    logout, generate_signature, fetch_account_info, fetch_current_holdings,
    backtest, fetch_historical_data
)

# Initialize session state for viewport width
if "viewport_width" not in st.session_state:
    st.session_state["viewport_width"] = streamlit_js_eval(js_expressions="window.innerWidth", key="ViewportWidth")

viewport_width = st.session_state["viewport_width"]

# Calculate column widths based on viewport width
col1_width = viewport_width * 0.25 if viewport_width else 300
col2_width = viewport_width * 0.50 if viewport_width else 600
col3_width = viewport_width * 0.25 if viewport_width else 300

# State Management
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = pd.DataFrame()

# Sidebar for login/logout and account information
with st.sidebar:
    if st.session_state.logged_in:
        st.success("Logged in successfully!")
        
        if 'account_info' not in st.session_state:
            st.session_state.account_info = fetch_account_info(st.secrets["api"]["robinhood_key"], st.secrets["api"]["robinhood_private_key"])
        
        if st.session_state.account_info:
            st.subheader("Account Information")
            st.write(f"Account Number: {st.session_state.account_info['account_number']}")
            st.write(f"Buying Power: {st.session_state.account_info['buying_power']} {st.session_state.account_info['buying_power_currency']}")
        
        if st.button("Logout"):
            logout()
    else:
        st.warning("Not logged in.")
        if st.button("Login"):
            st.session_state.logged_in = True
            st.session_state.account_info = fetch_account_info(st.secrets["api"]["robinhood_key"], st.secrets["api"]["robinhood_private_key"])

# Main layout with three columns
col1, col2, col3 = st.columns([col1_width, col2_width, col3_width])

with col3:  # Swap Current Holdings to the right column
    st.header("Current Holdings")
    if st.session_state.logged_in:
        if 'holdings_data' not in st.session_state:
            st.session_state.holdings_data = fetch_current_holdings(st.secrets["api"]["robinhood_key"], st.secrets["api"]["robinhood_private_key"])
        
        if st.session_state.holdings_data:
            df = pd.DataFrame(st.session_state.holdings_data)
            st.write("DataFrame structure:")
            st.write(df.head())  # Display the structure of the DataFrame
            total_value = df['value'].sum() if 'value' in df.columns else 0
            cash_available = float(st.session_state.account_info['buying_power'])
            total_value += cash_available
            st.subheader(f"Total Value: ${total_value:,.2f}")
            st.write(f"Cash Available: ${cash_available:,.2f}")
            st.dataframe(df)
    else:
        st.warning("Please log in to see your holdings.")

with col2:  # Algorithm Selection remains in the center column
    st.header("Algorithm Selection")
    algorithms = ["BollingerBands"]
    selected_algorithm = st.selectbox("Select an Algorithm", algorithms)
    if st.button("Run Algorithm"):
        result = subprocess.run(["python3", f"../python_algorithms/{selected_algorithm}.py"], capture_output=True, text=True)
        st.text(result.stdout)
    if st.button("Backtest"):
        symbol = "ETH-USD"
        interval = "5m"
        start = "2023-01-01"
        end = "2023-12-31"
        period = 20
        initial_cash = 10000
        trades_df = backtest(
            st.secrets["api"]["robinhood_key"], 
            st.secrets["api"]["robinhood_private_key"], 
            symbol, interval, start, end, period, initial_cash
        )
        st.write("Backtest Results")
        if not trades_df.empty:
            st.dataframe(trades_df)
            # Visualize monthly returns
            monthly_returns = trades_df.set_index('month')['return']
            st.bar_chart(monthly_returns)

with col1:  # Swap Account Summary to the left column
    st.header("Account Summary")
    if st.session_state.logged_in and st.session_state.account_info:
        st.write(f"Account Number: {st.session_state.account_info['account_number']}")
        st.write(f"Buying Power: {st.session_state.account_info['buying_power']} {st.session_state.account_info['buying_power_currency']}")
    else:
        st.error("Failed to fetch account information.")

# Full-width table to display historical data
st.header("Historical Data")
if st.session_state.logged_in:
    if st.button("Fetch Historical Data"):
        symbol = "ETH-USD"
        interval = "5m"
        start = "2023-01-01"
        end = "2023-12-31"
        st.session_state.historical_data = fetch_historical_data(
            st.secrets["api"]["robinhood_key"], 
            st.secrets["api"]["robinhood_private_key"], 
            symbol, interval, start, end
        )
    if not st.session_state.historical_data.empty:
        st.dataframe(st.session_state.historical_data)
else:
    st.warning("Please log in to fetch historical data.")
