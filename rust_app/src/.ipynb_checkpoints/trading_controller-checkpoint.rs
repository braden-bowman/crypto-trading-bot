use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Deserialize)]
struct Secrets {
    api: ApiSecrets,
}

#[derive(Deserialize)]
struct ApiSecrets {
    robinhood_key: String,
    robinhood_private_key: String,
}

#[derive(Serialize, Deserialize)]
struct TradeParameters {
    symbol: String,
    quantity: f64,
    order_type: String,
    side: String,
}

pub async fn execute_trade() {
    let secrets: Secrets = toml::from_str(
        &fs::read_to_string("/root/.streamlit/secrets.toml").expect("Failed to read secrets file"),
    )
    .expect("Failed to parse secrets file");

    let api_key = secrets.api.robinhood_key;
    let private_key = secrets.api.robinhood_private_key;

    // Replace this with the actual logic to determine trade parameters
    let trade_params = get_trade_parameters().await;

    if let Some(params) = trade_params {
        if validate_trade(&params).await {
            perform_trade(&api_key, &private_key, &params).await;
        }
    }
}

pub async fn test_mode() {
    let secrets: Secrets = toml::from_str(
        &fs::read_to_string("/root/.streamlit/secrets.toml").expect("Failed to read secrets file"),
    )
    .expect("Failed to parse secrets file");

    let api_key = secrets.api.robinhood_key;
    let private_key = secrets.api.robinhood_private_key;

    // Buy $1 of Ethereum
    let buy_params = TradeParameters {
        symbol: "ETH-USD".to_string(),
        quantity: 1.0 / get_eth_price().await,
        order_type: "market".to_string(),
        side: "buy".to_string(),
    };

    if validate_trade(&buy_params).await {
        perform_trade(&api_key, &private_key, &buy_params).await;
    }

    // Sell the purchased Ethereum
    let sell_params = TradeParameters {
        symbol: "ETH-USD".to_string(),
        quantity: buy_params.quantity,
        order_type: "market".to_string(),
        side: "sell".to_string(),
    };

    if validate_trade(&sell_params).await {
        perform_trade(&api_key, &private_key, &sell_params).await;
    }
}

async fn get_trade_parameters() -> Option<TradeParameters> {
    // Placeholder: Replace with logic to get trade parameters from the Python script
    Some(TradeParameters {
        symbol: "BTC-USD".to_string(),
        quantity: 0.1,
        order_type: "market".to_string(),
        side: "buy".to_string(),
    })
}

async fn validate_trade(_params: &TradeParameters) -> bool {
    // Implement validation logic, e.g., checking available funds
    // Placeholder: Always returns true for now
    true
}

async fn perform_trade(api_key: &str, private_key: &str, params: &TradeParameters) {
    let client = Client::new();

    let url = "https://trading.robinhood.com/api/v1/crypto/trading/orders/";
    let res = client
        .post(url)
        .json(&params)
        .header("x-api-key", api_key)
        .send()
        .await;

    match res {
        Ok(response) => {
            println!("Trade executed: {:?}", response);
        }
        Err(e) => {
            eprintln!("Failed to execute trade: {}", e);
        }
    }
}

async fn get_eth_price() -> f64 {
    // Placeholder: Implement a function to get the current price of Ethereum
    3000.0 // Example price, replace with actual price fetching logic
}
