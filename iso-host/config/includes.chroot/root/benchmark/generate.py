from dataclasses import dataclass, replace
from configuration import BASELINE

@dataclass
class Experiment:
    vpn: str = BASELINE["vpn"]
    delay: str = BASELINE["delay"]
    jitter: str = BASELINE["jitter"]
    loss: str = BASELINE["loss"]
    cpu_freq: str = BASELINE["cpu_freq"]
    core_count: int = BASELINE["core_count"]

def map_experiments(experiments: list[Experiment]) -> list[Experiment]:
    return [
        replace(exp, vpn=vpn)
        for exp in experiments
        for vpn in ["none", "wireguard", "nebula", "openvpn"]
    ]

flat_experiments = [
        Experiment(),
        Experiment(delay="10ms"),
        Experiment(delay="20ms"),
        Experiment(delay="30ms"),
        Experiment(delay="40ms"),
        Experiment(delay="50ms"),
        Experiment(delay="100ms"),
        Experiment(delay="200ms"),
        Experiment(delay="300ms"),
        Experiment(delay="100ms", jitter="1ms"),
        Experiment(delay="100ms", jitter="5ms"),
        Experiment(delay="100ms", jitter="10ms"),
        Experiment(delay="100ms", jitter="20ms"),
        Experiment(delay="100ms", jitter="50ms"),
        Experiment(delay="100ms", jitter="80ms"),
        Experiment(loss="0.1%"),
        Experiment(loss="0.2%"),
        Experiment(loss="0.4%"),
        Experiment(loss="0.8%"),
        Experiment(loss="1.6%"),
        Experiment(loss="3.2%"),
        Experiment(cpu_freq="3.0GHz"),
        Experiment(cpu_freq="2.0GHz"),
        Experiment(cpu_freq="1.0GHz"),
        Experiment(core_count=3),
        Experiment(core_count=2),
        Experiment(core_count=1),
    ]