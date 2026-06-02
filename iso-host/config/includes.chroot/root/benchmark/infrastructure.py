from time import sleep
from configuration import BASELINE, CLIENT_SSH, SERVER_SSH, ROUTER_SSH, GUEST_CAPPED_CORES, ROUTER_CLIENT_LAN_INTERFACE, ROUTER_SERVER_LAN_INTERFACE
from generate import Experiment
from shell import shell_on_guest, shell_on_host

current_experiment: Experiment = Experiment()

def _apply_network_impairments(delay, jitter, loss):
    shell_on_guest(ROUTER_SSH, f"tc qdisc replace dev {ROUTER_SERVER_LAN_INTERFACE} root netem delay {delay} {jitter} loss {loss} limit 100000")
    shell_on_guest(ROUTER_SSH, f"tc qdisc replace dev {ROUTER_CLIENT_LAN_INTERFACE} root netem delay {delay} {jitter} loss {loss} limit 100000")

def _lift_network_impairments():
    shell_on_guest(ROUTER_SSH, f"tc qdisc del dev {ROUTER_SERVER_LAN_INTERFACE} root")
    shell_on_guest(ROUTER_SSH, f"tc qdisc del dev {ROUTER_CLIENT_LAN_INTERFACE} root")

def _set_cpu_freq(freq):
    shell_on_host(f"cpupower -c {GUEST_CAPPED_CORES} frequency-set --min {freq} > /dev/null 2>&1", False)
    shell_on_host(f"cpupower -c {GUEST_CAPPED_CORES} frequency-set --max {freq} > /dev/null 2>&1", False)

def _recreate_domains(count):
    # Destroy guests
    shell_on_host(f"virsh destroy router", False)
    shell_on_host(f"virsh destroy client", False)
    shell_on_host(f"virsh destroy server", False)

    # Reconfigure core count
    shell_on_host(f"virsh setvcpus client {count} --config")
    shell_on_host(f"virsh setvcpus server {count} --config")

    # Start guests
    shell_on_host(f"virsh start router")
    shell_on_host(f"virsh start client")
    shell_on_host(f"virsh start server")

    # Wait for guests to come online
    shell_on_host(f"until ssh -o ConnectTimeout=1 -o BatchMode=yes router exit; do sleep 1; done", capture=True)
    shell_on_host(f"until ssh -o ConnectTimeout=1 -o BatchMode=yes client exit; do sleep 1; done", capture=True)
    shell_on_host(f"until ssh -o ConnectTimeout=1 -o BatchMode=yes server exit; do sleep 1; done", capture=True)


def _manage_vpn(vpn: str, up: bool):
    if vpn == "wireguard":
        if up:
            shell_on_guest(SERVER_SSH, "wg-quick up /etc/wireguard/server/wg0.conf")
            shell_on_guest(CLIENT_SSH, "wg-quick up /etc/wireguard/client/wg0.conf")
        else:
            shell_on_guest(CLIENT_SSH, "wg-quick down /etc/wireguard/client/wg0.conf")
            shell_on_guest(SERVER_SSH, "wg-quick down /etc/wireguard/server/wg0.conf")
    if vpn == "nebula":
        if up:
            shell_on_guest(SERVER_SSH, "nohup nebula -config /etc/nebula/server/config.yml > /dev/null 2>&1 &")
            shell_on_guest(CLIENT_SSH, "nohup nebula -config /etc/nebula/client/config.yml > /dev/null 2>&1 &")
        else:
            shell_on_guest(CLIENT_SSH, "pkill nebula", check=False, capture=True)
            shell_on_guest(SERVER_SSH, "pkill nebula", check=False, capture=True)
    if vpn == "openvpn":
        if up:
            shell_on_guest(SERVER_SSH, "openvpn --config /etc/openvpn/server/server.conf --daemon")
            shell_on_guest(CLIENT_SSH, "openvpn --config /etc/openvpn/client/client.ovpn --daemon")
        else:
            shell_on_guest(CLIENT_SSH, "pkill openvpn", check=False, capture=True)
            shell_on_guest(SERVER_SSH, "pkill openvpn", check=False, capture=True)
    sleep(5)

def preconfigure_host():
    # Disable Intel Turbo Boost
    shell_on_host("echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo", check=False, capture=True)

    # Disable AMD/generic CPU Boost
    shell_on_host("echo 0 > /sys/devices/system/cpu/cpufreq/boost", check=False, capture=True)

    # Lock CPU governor to performance
    shell_on_host("cpupower frequency-set --governor performance1", check=False, capture=True)

    # Flush infrastructure
    _recreate_domains(BASELINE["core_count"])

def update_infrastructure(experiment: Experiment):
    global current_experiment
    ce = current_experiment

    # Recreate with new core count if required
    if ce.core_count != experiment.core_count:
        _recreate_domains(experiment.core_count)
        ce = Experiment()

    # Configure VPN if required
    if ce.vpn != experiment.vpn:
        # If any curently running, stop it
        if ce.vpn != "none": _manage_vpn(ce.vpn, False)
        # Start new if requested
        if experiment.vpn != "none": _manage_vpn(experiment.vpn, True)

    # Configure CPU frequency
    if ce.cpu_freq != experiment.cpu_freq:
        _set_cpu_freq(experiment.cpu_freq)

    # Configure network imapirments
    if ce.delay != experiment.delay or ce.jitter != experiment.jitter or ce.loss != experiment.loss:
        _apply_network_impairments(experiment.delay, experiment.jitter, experiment.loss)

    current_experiment = experiment