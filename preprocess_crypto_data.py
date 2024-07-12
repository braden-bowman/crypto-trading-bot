import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def preprocess_data(file_name, output_file):
    # Load the data
    data = pd.read_csv(file_name)

    # Check if data is loaded properly
    if data.empty:
        raise ValueError("The data frame is empty. Please check the data download step.")

    # Calculate additional features
    data['MA_10'] = data['close'].rolling(window=10).mean()
    data['MA_50'] = data['close'].rolling(window=50).mean()
    data = data.dropna()

    # Check if there are enough data points after calculating moving averages
    if data.empty:
        raise ValueError("The data frame is empty after calculating moving averages. Please check the date range and data availability.")

    # Preprocess the data
    features = ['close', 'volume', 'MA_10', 'MA_50']
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data[features])
    
    # Save preprocessed data
    pd.DataFrame(scaled_data, columns=features).to_csv(output_file, index=False)
    print(f"Data preprocessed and saved to {output_file}")

if __name__ == "__main__":
    input_file = 'crypto_data.csv'
    output_file = 'preprocessed_crypto_data.csv'
    preprocess_data(input_file, output_file)
