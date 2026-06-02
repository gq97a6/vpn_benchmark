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

flat_experiments = [
        Experiment(), # Baseline 1
        Experiment(delay="50ms"), # Cross-country / inter-state
        Experiment(delay="100ms"), # Transatlantic
        Experiment(delay="300ms"), # Satellite / terrible LTE
        Experiment(delay="100ms", jitter="20ms"), # Normal wireless variance
        Experiment(delay="100ms", jitter="80ms"), # Extreme out-of-order delivery
        Experiment(loss="0.1%"), # Bad cable
        Experiment(loss="1.0%"), # Overloaded neighborhood node
        Experiment(loss="3.0%"), # Virtually dead for TCP bulk transfer
        Experiment(core_count=1, cpu_freq="2.0GHz"), # The Low-End Box 1
        Experiment(core_count=2, cpu_freq="2.0GHz"), # The Low-End Box 2
    ]