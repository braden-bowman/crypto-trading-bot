#!/bin/bash

# Function to create files and directories
create_file() {
  mkdir -p "$(dirname "$1")"
  echo "$2" > "$1"
}

# Function to install Docker
install_docker() {
  if ! command -v docker &> /dev/null
  then
    echo "Docker not found. Installing..."
    sudo apt remove -y docker docker-engine docker.io containerd runc
    sudo apt update
    sudo apt install -y \
      ca-certificates \
      curl \
      gnupg \
      lsb-release

    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
  else
    echo "Docker is already installed."
  fi
}

# Function to install Docker Compose
install_docker_compose() {
  if ! command -v docker-compose &> /dev/null
  then
    echo "Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.16.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    if [ ! -f /usr/bin/docker-compose ]; then
      sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
    else
      echo "/usr/bin/docker-compose already exists. Skipping symlink creation."
    fi
  else
    echo "Docker Compose is already installed."
  fi
}

# Function to install NVIDIA Container Toolkit
install_nvidia_toolkit() {
  if ! dpkg-query -W nvidia-container-toolkit &> /dev/null
  then
    echo "NVIDIA Container Toolkit not found. Installing..."
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    sudo apt update
    sudo apt install -y nvidia-docker2
    sudo systemctl restart docker
  else
    echo "NVIDIA Container Toolkit is already installed."
  fi
}

# Install Docker, Docker Compose, and NVIDIA Container Toolkit if not installed
install_docker
install_docker_compose
install_nvidia_toolkit

# Ensure Docker daemon is running
sudo systemctl start docker

# Pull necessary Docker images
docker pull rust:latest
docker pull nvidia/cuda:11.8.0-base-ubuntu22.04
docker pull python:3.10

# Project directories
mkdir -p crypto-trading-bot/{rust_app/src,python_algorithms,streamlit_app}

# Create Rust files
create_file "crypto-trading-bot/rust_app/Cargo.toml" '[package]
name = "crypto_trading_bot"
version = "0.1.0"
edition = "2018"

[dependencies]
pyo3 = { version = "0.15.1", features = ["extension-module"] }
'

create_file "crypto-trading-bot/rust_app/src/main.rs" 'fn main() {
    println!("Hello, crypto trading bot!");
}
'

create_file "crypto-trading-bot/rust_app/src/lib.rs" 'use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn run_algorithm(name: &str) -> PyResult<()> {
    let script_path = format!("./python_algorithms/{}.py", name);
    let output = std::process::Command::new("python3")
        .arg(script_path)
        .output()
        .expect("Failed to execute algorithm");
    println!("Algorithm output: {:?}", output);
    Ok(())
}

#[pymodule]
fn crypto_trading_bot(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_algorithm, m)?)?;
    Ok(())
}
'

# Create Python algorithm files
create_file "crypto-trading-bot/python_algorithms/algorithm1.py" 'import polars as pl
import torch

def main():
    print("Running Algorithm 1")

if __name__ == "__main__":
    main()
'

create_file "crypto-trading-bot/python_algorithms/algorithm2.py" 'import polars as pl
import torch

def main():
    print("Running Algorithm 2")

if __name__ == "__main__":
    main()
'

# Create Streamlit app files
create_file "crypto-trading-bot/streamlit_app/app.py" 'import streamlit as st
import subprocess

algorithms = ["algorithm1", "algorithm2"]

st.title("Crypto Trading Bot")
selected_algorithm = st.selectbox("Select an Algorithm", algorithms)

if st.button("Run Algorithm"):
    result = subprocess.run(["python3", f"../python_algorithms/{selected_algorithm}.py"], capture_output=True, text=True)
    st.text(result.stdout)
'

create_file "crypto-trading-bot/streamlit_app/requirements.txt" 'streamlit
'

create_file "crypto-trading-bot/streamlit_app/Dockerfile" 'FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "app.py"]
'

# Create Dockerfile
create_file "crypto-trading-bot/Dockerfile" 'FROM rust:latest AS builder
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
'

# Create docker-compose.yml
create_file "crypto-trading-bot/docker-compose.yml" 'version: "3.9"

services:
  trading-bot:
    build: .
    volumes:
      - ./python_algorithms:/app/python_algorithms
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  streamlit:
    build:
      context: ./streamlit_app
    ports:
      - "8501:8501"
    volumes:
      - ./python_algorithms:/app/python_algorithms
'

# Print completion message
echo "Project setup complete. Navigate to the crypto-trading-bot directory and run 'docker compose up --build' to start the services."
