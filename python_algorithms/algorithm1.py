import json

def main():
    trade_params = {
        "symbol": "BTC-USD",
        "quantity": 0.1,
        "order_type": "market",
        "side": "buy"
    }
    print(json.dumps(trade_params))

if __name__ == "__main__":
    main()
