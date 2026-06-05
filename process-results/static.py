from pathlib import Path

project_dir = Path("C:\\sync\\projects\\vpn_benchmark\\process-results")

thresholds = {
    "down": 10,
    "up": 10,
    "ping": 3,
    "cpu": 5,
}

key_cols = ["vpn", "delay", "jitter", "loss", "cpu_freq", "core_count"]

data_cols =  [
    col + suf
    for col in ["down", "up", "ping",  "cpu", "efficiency"]
    for suf in ["_mean", "_rsd", "_sd"]
]

cols_to_keep = key_cols + data_cols