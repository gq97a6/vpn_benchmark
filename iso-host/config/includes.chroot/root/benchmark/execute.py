import json
from dataclasses import asdict
from time import sleep
from configuration import SERVER_SSH, CLIENT_SSH, IP_SERVER
from generate import Experiment
from shell import shell_on_guest, shell_on_host
from infrastructure import update_infrastructure

def _begin_monitoring(results_folder):
    shell_on_guest(CLIENT_SSH, f"sar -u ALL -o {results_folder}/cpu.bin 1 >/dev/null 2>&1 &")

def _stop_monitoring(results_folder):
    # Stop sar
    shell_on_guest(CLIENT_SSH, "pkill sar", check=False, capture=True)
    # Convert binary to csv
    shell_on_guest(CLIENT_SSH, f"sadf -d {results_folder}/cpu.bin > {results_folder}/cpu.csv")
    # Remove binary
    shell_on_guest(CLIENT_SSH, f"rm {results_folder}/cpu.bin")

def _execute_experiment(experiment: Experiment, root_results_folder, index):

    results_folder = f"{root_results_folder}/{index}"

    # Prepare infrastructure
    update_infrastructure(experiment)

    # Create results folder
    shell_on_guest(CLIENT_SSH, f"mkdir -p {results_folder}")

    # Start servers
    shell_on_guest(SERVER_SSH, "netserver > /dev/null 2>&1 &")
    shell_on_guest(SERVER_SSH, "iperf3 -s > /dev/null 2>&1 &")

    # Benchmark
    _begin_monitoring(results_folder)
    shell_on_guest(CLIENT_SSH, f"flent rrul -H {IP_SERVER[experiment.vpn]} -l 60 -D {results_folder}")
    shell_on_guest(CLIENT_SSH, f"iperf3 -c {IP_SERVER[experiment.vpn]} -t 60 -J --logfile {results_folder}/iperf.json")
    _stop_monitoring(results_folder)

    # Stop servers
    shell_on_guest(SERVER_SSH, "pkill iperf3", check=False, capture=True)
    shell_on_guest(SERVER_SSH, "pkill netserver", check=False, capture=True)

    # Extract results to host
    shell_on_host(f"scp -r {CLIENT_SSH}:{results_folder} {root_results_folder}") 

    # Cooldown delay before next experiment
    sleep(1)

def execute_experiments(experiments: list[Experiment], root_results_folder: str):
    # Create root results folder on host
    shell_on_host(f"mkdir -p {root_results_folder}")

    # Dump experiments table to file on host
    with open(f"{root_results_folder}/metadata.json", "w") as f:
        json.dump([asdict(exp) for exp in experiments], f)

    # Run every experiment
    for index, experiment in enumerate(experiments):
        print(f"====================================")
        print(f"PROGRESS: {index} out of {len(experiments)}")
        print(f"====================================")
        _execute_experiment(experiment, root_results_folder, index)
