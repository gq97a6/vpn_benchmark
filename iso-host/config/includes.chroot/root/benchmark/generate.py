from dataclasses import dataclass, replace
from configuration import BASELINE
import random

@dataclass
class Experiment:
    vpn: str = BASELINE["vpn"]
    delay: str = BASELINE["delay"]
    jitter: str = BASELINE["jitter"]
    loss: str = BASELINE["loss"]
    cpu_freq: str = BASELINE["cpu_freq"]
    core_count: int = BASELINE["core_count"]

def map_experiments(experiments: list[Experiment], repeat_count: int) -> list[Experiment]:
    exps = [
        replace(exp, vpn=vpn)
        for exp in experiments
        for _ in range(repeat_count)
        for vpn in ["none", "wireguard", "nebula", "openvpn"]
    ]

    random.shuffle(exps)
    return exps


@dataclass
class Experiment:
    vpn: str = BASELINE["vpn"]
    bandwidth: str = BASELINE["bandwidth"]
    delay: str = BASELINE["delay"]
    jitter: str = BASELINE["jitter"]
    loss: str = BASELINE["loss"]
    cpu_freq: str = BASELINE["cpu_freq"]
    core_count: int = BASELINE["core_count"]

flat_experiments = [
    Experiment(), # Baseline
    Experiment(bandwidth="1000mbit", delay="20ms", jitter="5ms", loss="0.1%"), # Realistic average residential fiber
    Experiment(delay="50ms", jitter="10ms"), # Cryptographic sliding window stress (out-of-order)
    Experiment(delay="100ms"), # Trans-Atlantic link (BDP stress)
    Experiment(core_count=1, cpu_freq="1.5GHz"), # Context-switch and crypto-threading starvation
    Experiment(core_count=2, cpu_freq="2.0GHz"), # Low-end VPS tier
]