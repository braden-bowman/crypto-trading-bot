# Crypto Trading Bot

This project is a crypto trading bot that connects to your Robinhood account and allows you to manage your holdings and run trading algorithms.

## Setup Instructions

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/crypto-trading-bot.git
    cd crypto-trading-bot
    ```

2. Build and run the Docker container:
    ```sh
    docker compose up --build
    ```

3. Open the Streamlit app in your browser:
    ```
    http://localhost:8501
    ```

4. Login with your Robinhood credentials.

### Disabling Two-Factor Authentication (2FA)

If you do not want to use 2FA with your Robinhood account, you can disable it by following these steps:

1. Log in to your Robinhood account on the web or mobile app.
2. Go to `Settings`.
3. Navigate to `Security & Privacy`.
4. Turn off `Two-Factor Authentication`.

> **Note:** Disabling 2FA reduces the security of your account. It is highly recommended to keep 2FA enabled to protect your account from unauthorized access.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
