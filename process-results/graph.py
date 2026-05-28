import gzip
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional

@dataclass
class Experiment:
    id: int
    vpn: str
    delay: str
    jitter: str
    loss: str
    cpu_freq: str
    core_count: int
    iperf_data: Optional[Dict[str, Any]] = None
    flent_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_json(cls, idx: int, data: Dict[str, Any]):
        return cls(id=idx, **data)

# Load JSON regardless of whether it is gzipped.
def load_json_file(path: Path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_results(root_dir: str) -> List[Experiment]:
    root = Path(root_dir)
    metadata_path = root / "metadata.json"
    
    with metadata_path.open("r") as f:
        meta_list = json.load(f)

    experiments = []
    for idx, meta in enumerate(meta_list):
        exp = Experiment.from_json(idx, meta)

        exp_dir = root / str(idx)
        if not exp_dir.is_dir():
            experiments.append(exp)
            continue

        iperf_file = exp_dir / "iperf.json"
        if iperf_file.exists():
            exp.iperf_data = load_json_file(iperf_file)

        flent_files = list(exp_dir.glob("*.flent.gz"))
        if flent_files:
            exp.flent_data = load_json_file(flent_files[0])

        experiments.append(exp)
    return experiments

# Prints a summary table of throughput.
def summarize_results(experiments: List[Experiment]):
    print(f"{'ID':<4} | {'VPN':<12} | {'Delay':<8} | {'Loss':<6} | {'Throughput (Mbps)':<15}")
    print("-" * 55)

    for e in experiments:
        throughput = "N/A"
        if e.iperf_data and "end" in e.iperf_data:
            bps = e.iperf_data["end"].get("sum_received", {}).get("bits_per_second", 0)
            throughput = f"{bps / 1_000_000:.2f}"
        print(f"{e.id:<4} | {e.vpn:<12} | {e.delay:<8} | {e.loss:<6} | {throughput:<15}")

def main():
    results_path = "./results"
    experiments = load_results(results_path)
    summarize_results(experiments)

if __name__ == "__main__":
    main()