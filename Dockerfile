FROM rust:latest AS builder
WORKDIR /usr/src/app
COPY rust_app/Cargo.toml ./
COPY rust_app/src ./src
RUN ["bash", "-c", "if [ ! -f Cargo.lock ]; then cargo generate-lockfile; fi"]
RUN cargo build --release

FROM nvidia/cuda:11.8.0-base-ubuntu22.04
WORKDIR /app
COPY --from=builder /usr/src/app/target/release/crypto_trading_bot ./
COPY python_algorithms ./python_algorithms

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install polars torch

CMD ["./crypto_trading_bot"]

