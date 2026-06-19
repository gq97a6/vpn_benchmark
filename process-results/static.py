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
experiment_groups = {
    "baseline": {
        "mask": (0, 0, 0, 0, 4.0, 4),
        "cols": ["bandwidth", "delay", "jitter", "loss", "vpn"],
        "desc": "Baseline"
    },
    "residential_fiber": {
        "mask": (300, 20, 5, 0.1, 4.0, 4),
        "cols": ["bandwidth", "delay", "jitter", "loss", "vpn"],
        "desc": "Realistic average residential fiber (300 MBps | 20 ms delay | 5 ms jitter | 0.1% loss)"
    },
    "extreme_ooo": {
        "mask": (0, 20, 50, 0.0, 4.0, 4),
        "cols": ["delay", "jitter", "vpn"],
        "desc": "Cryptographic sliding window stress (20 ms delay | 50 ms jitter)"
    },
    "retransmission": {
        "mask": (0, 100, 0, 2.0, 4.0, 4),
        "cols": ["delay", "loss", "vpn"],
        "desc": "TCP retransmission overhead amplification (100 ms delay | 2% loss)"
    },
    "starvation": {
        "mask": (0, 0, 0, 0.0, 1.5, 1),
        "cols": ["cpu_freq", "core_count", "vpn"],
        "desc": "Context-switch and crypto-threading starvation (1.5 GHz | 1 core)"
    },
    "low_end_vps": {
        "mask": (0, 0, 0, 0.0, 2.0, 2),
        "cols": ["cpu_freq", "core_count", "vpn"],
        "desc": "Low-end VPS tier (2.0 GHz | 2 core)"
    },
    "bufferbloat": {
        "mask": (50, 10, 0, 0.0, 4.0, 4),
        "cols": ["bandwidth", "delay", "vpn"],
        "desc": "Bufferbloat / narrow pipe queue saturation (50 MBps | 10 ms delay)"
    },
}