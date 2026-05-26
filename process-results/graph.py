import gzip
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Experiment:
    delay: str
    jitter: str
    loss: str
    cpu: str
    iperf: dict
    flent: dict


def load_flent(path: Path) -> dict:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_iperf(path: Path) -> dict:
    with path.open("r") as f:
        return json.load(f)


def load_metadata(path: Path) -> list[Experiment]:
    with (path / "metadata.json").open("r") as f:
        return [Experiment(**d) for d in json.load(f)]


def load_all(path: str) -> list[Experiment]:
    path = Path(path)
    experiments = load_metadata(path)

    for vpn in ["wireguard", "nebula", "openvpn"]:
        vpn_dir = path / vpn

        for iperf_file in (vpn_dir / "iperf").glob("*.json"):
            idx = int(iperf_file.stem)
            experiments[idx].iperf[vpn] = load_iperf(iperf_file)

        for flent_file in (vpn_dir / "flent").glob("*.flent.gz"):
            data = load_flent(flent_file)
            idx = int(data["metadata"]["TITLE"])
            experiments[idx].flent[vpn] = data

    return experiments


def print_experiments(experiments: list[Experiment]) -> None:
    for e in experiments:
        print(e.delay, e.jitter, e.loss, end=";", sep=";")

        for vpn in ["wireguard", "nebula", "openvpn"]:
            print(int(e.iperf[vpn]["end"]["sum_received"]["bits_per_second"] / 1000000), end=";", sep=";")
        print()


def main():
    print_experiments(load_all("/benchmark_results/core105"))
    print_experiments(load_all("/benchmark_results/core205"))
    print_experiments(load_all("/benchmark_results/core110"))
    print_experiments(load_all("/benchmark_results/core210"))
    print_experiments(load_all("/benchmark_results/core120"))
    print_experiments(load_all("/benchmark_results/core220"))


if __name__ == "__main__":
    main()
