from pathlib import Path

project_dir = Path("C:\\sync\\projects\\vpn_benchmark\\process-results")

thresholds = {
    "down": 10,
    "up": 10,
    "ping": 3,
    "cpu": 5,
}

key_cols = ["vpn", "bandwidth", "delay", "jitter", "loss", "cpu_freq", "core_count"]

data_cols =  [
    col + suf
    for col in ["down", "up", "ping",  "cpu", "efficiency"]
    for suf in ["_mean", "_rsd", "_sd"]
]

cols_to_keep = key_cols + data_cols

# (bandwidth, delay, jitter, loss, cpu_freq, core_count)
experiment_groups = [
    # Realistic average residential fiber
    (
        [(0, 0, 0, 0.0, 4.0, 4), (300, 20, 5, 0.1, 4.0, 4)],
        ["bandwidth", "delay", "jitter", "loss", "vpn"],
        "residential_fiber"
    ),
    # Cryptographic sliding window stress (heavy out-of-order)
    (
        [(0, 0, 0, 0.0, 4.0, 4), (0, 20, 50, 0.0, 4.0, 4)],
        ["delay", "jitter", "vpn"],
        "extreme_ooo"
    ),
    # TCP retransmission overhead amplification
    (
        [(0, 0, 0, 0.0, 4.0, 4), (0, 100, 0, 2.0, 4.0, 4)],
        ["delay", "loss", "vpn"],
        "retransmission"
    ),
    # Context-switch and crypto-threading starvation
    (
        [(0, 0, 0, 0.0, 4.0, 4), (0, 0, 0, 0.0, 1.5, 1)],
        ["cpu_freq", "core_count", "vpn"],
        "starvation"
    ),
    # Low-end VPS tier
    (
        [(0, 0, 0, 0.0, 4.0, 4), (0, 0, 0, 0.0, 2.0, 2)],
        ["cpu_freq", "core_count", "vpn"],
        "low_end_vps"
    ),
    # Bufferbloat / narrow pipe queue saturation
    (
        [(0, 0, 0, 0.0, 4.0, 4), (50, 10, 0, 0.0, 4.0, 4)],
        ["bandwidth", "delay", "vpn"],
        "bufferbloat"
    ),
]