QEMU_DIR="iso-host/config/includes.chroot/qemu"
BENCHMARK_DIR="iso-host/config/includes.chroot/root/benchmark"

# Make sure networks are up
for net in lan0 lan1 mgmt0
do
    virsh net-define $QEMU_DIR/network/$net.xml &> /dev/null;
    virsh net-start $net &> /dev/null;
done

# Define domains
for domain in router server client
do
    virsh define $QEMU_DIR/domain/$domain.xml &> /dev/null;
done

# Run benchmark
cd "$BENCHMARK_DIR"
python3 main.py