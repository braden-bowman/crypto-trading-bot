import streamlit as st
import subprocess

algorithms = ["algorithm1", "algorithm2"]

st.title("Crypto Trading Bot")
selected_algorithm = st.selectbox("Select an Algorithm", algorithms)

if st.button("Run Algorithm"):
    result = subprocess.run(["python3", f"../python_algorithms/{selected_algorithm}.py"], capture_output=True, text=True)
    st.text(result.stdout)

