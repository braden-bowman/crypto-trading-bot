# Build stage for Rust application
FROM rust:latest AS builder
WORKDIR /usr/src/app
COPY rust_app/Cargo.toml ./
COPY rust_app/src ./src
RUN ["bash", "-c", "if [ ! -f Cargo.lock ]; then cargo generate-lockfile; fi"]
RUN cargo build --release

# Final stage with CUDA
FROM nvidia/cuda:11.8.0-base-ubuntu22.04
WORKDIR /app

# Install Python dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy Python dependencies file
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Copy built Rust application
COPY --from=builder /usr/src/app/target/release/crypto_trading_bot ./
COPY python_algorithms ./python_algorithms
COPY .streamlit/secrets.toml /root/.streamlit/secrets.toml

# Copy Streamlit application
COPY streamlit_app /app/streamlit_app

CMD ["streamlit", "run", "streamlit_app/app.py"]
