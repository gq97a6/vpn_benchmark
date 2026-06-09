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

# delay, jitter, loss, cpu_freq, core_count
filter_masks = [
    # 0. Delay in isolation
    # delay, vpn
    [(0, 0, 0, 4.0, 4), (50, 0, 0, 4.0, 4), (100, 0, 0, 4.0, 4), (300, 0, 0, 4.0, 4)],
    # 1. Real network conditions
    # delay, jitter, vpn
    [(0, 0, 0, 4.0, 4), (100, 20, 0, 4.0, 4), (100, 80, 0, 4.0, 4)],
    # 2. Packet loss in isolation
    # loss", vpn
    [(0, 0, 0, 4.0, 4), (0, 0, 0.1, 4.0, 4), (0, 0, 1.0, 4.0, 4), (0, 0, 3.0, 4.0, 4)],
    # 3. Lower tier / low-end machines
    # cpu_freq, core_count, vpn
    [(0, 0, 0, 4.0, 4), (0, 0, 0, 2.0, 1), (0, 0, 0, 2.0, 2)],
    # 4. Standard conditions
    # delay, jitter, loss, vpn
    [(0, 0, 0, 4.0, 4), (40, 10, 0.5, 4.0, 4)],
    # 5. Extreme out-of-order delivery
    # delay, jitter, vpn
    [(0, 0, 0, 4.0, 4), (100, 80, 0, 4.0, 4)],
]