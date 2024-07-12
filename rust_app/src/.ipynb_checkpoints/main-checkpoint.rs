use std::env;
use std::time::Duration;
use tokio::time;
use tokio::runtime::Runtime;

mod trading_controller;

fn main() {
    let args: Vec<String> = env::args().collect();
    let rt = Runtime::new().unwrap();
    rt.block_on(async {
        if args.contains(&"--test".to_string()) {
            trading_controller::test_mode().await;
        } else {
            loop {
                trading_controller::execute_trade().await;
                time::sleep(Duration::from_secs(1800)).await; // Adjust as necessary for your trade frequency
            }
        }
    });
}



// fn main() {
//     println!("Hello, crypto trading bot!");
// }

