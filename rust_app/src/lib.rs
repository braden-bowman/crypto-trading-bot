use pyo3::prelude::*;
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

