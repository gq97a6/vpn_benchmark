# Automated VPN benchmark

A highly reproducible, KVM-based testbed for benchmarking VPN protocols (Wireguard, Nebula, OpenVPN) under simulated hardware and network constraints. It uses custom Debian Live ISOs, strict CPU pinning, tc network degradation, and cpupower frequency capping to generate isolated metrics.

- Programming language - `Python`
- Tested protocols - `Wireguard`, `Nebula`, `OpenVPN`
- Used benchmark - `flent`
- Hypervisor - `KVM/QEMU`, `virsh`
- Network conditions degrading - `tc`
- CPU Clock rate capping - `cpupower`
- Live ISO - `live-build`

## Infrastructure

#### Virtual machines

- `Client`  ⇄ `Router` ⇄ `Server`

#### QEMU Networks

- ``mgmt0`` - Managment network for remote control over SSH
- ``lan0`` - LAN network between server and router
- ``lan1`` - LAN network between client and router

| Bridge     | Host interface | Guest interface | IP Address   | MAC Address       |
|------------|----------------|-----------------|--------------|-------------------|
| `br-mgmt0` | →              | →               | 10.0.0.1     | *auto-generated*  |
| →          | `router-mgmt0` | `mgmt0`         | 10.0.0.2     | 52:54:00:00:00:01 |
| →          | `server-mgmt0` | `mgmt0`         | 10.0.0.3     | 52:54:00:00:00:02 |
| →          | `client-mgmt0` | `mgmt0`         | 10.0.0.4     | 52:54:00:00:00:03 |
| `br-lan0`  | →              | →               | *not routed* | *auto-generated*  |
| →          | `router-lan0`  | `lan0`          | 10.0.10.1    | 52:54:00:10:00:01 |
| →          | `server-lan0`  | `lan0`          | 10.0.10.2    | 52:54:00:10:00:02 |
| `br-lan1`  | →              | →               | *not routed* | *auto-generated*  |
| →          | `router-lan1`  | `lan1`          | 10.0.20.1    | 52:54:00:20:00:01 |
| →          | `client-lan1`  | `lan1`          | 10.0.20.2    | 52:54:00:20:00:02 |

#### VPN Networks

| VPN         | Interface | Owner  | IP Address |
|-------------|-----------|--------|------------|
| `Wireguard` |           |        |            |
| →           | `wg0`     | Server | 10.10.0.1  |
| →           | `wg0`     | Client | 10.10.0.2  |
| `Nebula`    |           |        |            |
| →           | `neb0`    | Server | 10.20.0.1  |
| →           | `neb0`    | Client | 10.20.0.2  |
| `OpenVPN`   |           |        |            |
| →           | `tun0`    | Server | 10.30.0.1  |
| →           | `tun0`    | Client | 10.30.0.2  |

#### Precautions

* Diskless system (toram)
* Core pining for QEMU emulation
* Core isolation for QEMU guests
* CPU performance and frequency scaling disabled
* Randomized list of experiments to avoid thermal carryover
* TCP congestion control set to `bbr` for guests
* Per socket TCP buffers increased for guests
* Each VPN configured with 1420 MTU

## Experiments

Each experiment is set of conditions under which benchmarks are run:
```python
class Experiment:
    vpn: str = BASELINE["vpn"]
    bandwidth: str = BASELINE["bandwidth"]
    delay: str = BASELINE["delay"]
    jitter: str = BASELINE["jitter"]
    loss: str = BASELINE["loss"]
    cpu_freq: str = BASELINE["cpu_freq"]
    core_count: int = BASELINE["core_count"]
```

Each experiment is run for each protocol 10 times:
```python
Experiment(), # Baseline: Raw throughput capabilities
Experiment(bandwidth="300mbit", delay="20ms", jitter="5ms", loss="0.1%"), # Realistic average residential fiber
Experiment(delay="20ms", jitter="50ms"), # Cryptographic sliding window stress (heavy out-of-order)
Experiment(delay="100ms", loss="2.0%"), # TCP retransmission overhead amplification
Experiment(core_count=1, cpu_freq="1.5GHz"), # Context-switch and crypto-threading starvation
Experiment(core_count=2, cpu_freq="2.0GHz"), # Low-end VPS tier
Experiment(bandwidth="50mbit", delay="10ms"), # Bufferbloat / narrow pipe queue saturation
```

## Impairments

Network impairments (executed on router node):
```bash
# No shaping, just impairments
tc qdisc add dev {interface} root handle 1: netem delay {delay} {jitter} loss {loss} limit 5000

# With bandwidth limit
tc qdisc add dev {interface} root handle 1: tbf rate {bandwidth} burst 1mbit latency 50ms
tc qdisc add dev {interface} parent 1:1 handle 10: netem delay {delay} {jitter} loss {loss} limit 5000
```

CPU impairments (executed on host while nodes are destroyed):
```bash
# Core count
virsh setvcpus client {count} --config

# Frequency
cpupower -c {GUEST_CAPPED_CORES} frequency-set --min {freq}
```

## Methodology

#### 0. Initial steps

Variant A
1. Executing `test.sh`
1. QEMU networks and domains defining and starting

Variant B
1. Booting `host.iso`
1. Isolating cores dedicated for VMs
1. Autostarting QEMU networks and domains

#### 1. Core script initial steps

1. Executing `main.py`.
1. Attempt to disable CPU Boost and to lock CPU governor to performance.
1. Generate list of experiments and dump metadata to root results directory.

#### 2. Steps executed for every experiment

1. Configure core count assigned to VMs
1. Setup specific VPN
1. Configure CPU frequency of cores dedicated to client and server VMs
1. Configure network conditions
1. Begin `sar` monitoring
1. Run benchmarks
1. Stop `sar` monitoring
1. Extract results from client VM to host

## Results format

```txt
root_results_folder/
├── 0/
│   ├── rrul-2026-05-21T214911.731061.flent.gz
│   ├── cpu.csv
│   └── iperf.json
│── 1/
│   ├── rrul-2026-05-21T214911.731061.flent.gz
│   ├── cpu.csv
│   └── iperf.json
└── metadata.json
```

## Requirements

#### Hardware
- Hardware virtualization
- 24 CPU cores
    - 4 per VM
    - 4 for host
    - 4 for QEMU emulator threads

> [!TIP]
> To lower CPU core count requirement edit following
> - Core pining in domain XML configurations
> - Host core isolation configuration in boot parameters in `build.sh` for host ISO
> - `GUEST_CAPPED_CORES` and `BASELINE` in `configuration.py`
> - Experiments in `generate.py`

#### For running via ISO
``` bash
apt update && apt install -y live-build
```
1. Build `host.iso` with `build.sh`
1. Boot `host.iso`
1. Run `/root/benchmark/main.py`

#### For testing on current system
``` bash
apt update && apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virtinst virt-manager python3
```
1. Build `guest.iso` with `iso-guest/build.sh` and place it in `/qemu/guest.iso`
1. Clone SSH configuration from `iso-host/config/includes.chroot/root/.ssh`
1. Run `test.sh`

## Project structure
```bash
.
├── build.sh # Builds host.iso into root directory of project
├── test.sh # Runs benchmark localy (via QEMU virtual machines)
├── ai.sh # Dumps project and README.md for LLMs
├── iso-guest
│   ├── build.sh # Builds guest.iso into iso-guest directory
│   └── config # Live-build configuration
│       ├── hooks
│       │   ├── live
│       │   │   └── 0100-fastboot.hook.binary # Configure bootloaders to enable unattended boot
│       │   └── normal
│       │       ├── 0100-access.hook.chroot # Configure access
│       │       └── 0200-networkd.hook.chroot # Enable networkd and disable wait-online
│       └── includes.chroot
│           ├── etc
│           │   ├── nebula # VPN configuration for both sides
│           │   ├── openvpn # VPN configuration for both sides
│           │   ├── wireguard # VPN configuration for both sides
│           │   ├── sysctl.d # Enable routing, configure congestion control and buffers size
│           │   └── systemd/network # Defines all interfaces with static MAC addresses
│           └── root/.ssh # SSH configuration
├── iso-host
│   ├── build.sh
│   └── config
│       ├── hooks
│       │   ├── live
│       │   │   └── 0100-fastboot.hook.binary # Configure bootloaders to enable unattended boot
│       │   └── normal
│       │       ├── 0100-access.hook.chroot # Configure access
│       │       ├── 0200-networkd.hook.chroot # Enable networkd and disable wait-online
│       │       ├── 0300-virsh.hook.chroot # Configure infrastructure
│       └── includes.chroot
│           ├── qemu
│           │   ├── domain # QEMU domains in XML format
│           │   └── network # QEMU networks in XML format
│           │   └── guest.iso # Live ISO for guests (has to be build)
│           └── root
│               └── benchmark # Benchmark script
│                   ├── configuration.py # Static configuration
│                   ├── execute.py # Core benchmark
│                   ├── generate.py # Generate experiments
│                   ├── infrastructure.py # Control current state of infrastructure
│                   ├── main.py
│                   └── shell.py # Helper functions that execute shell commands on host/guest
└── process-results
    └── graph.py # Analyze results
```
