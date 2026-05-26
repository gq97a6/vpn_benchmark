bash iso-guest/build.sh
mv iso-guest/guest.iso iso-host/config/includes.chroot/qemu
rm -rf iso-host/config/includes.chroot/root/benchmark/__pycache__
bash iso-host/build.sh
mv iso-host/host.iso .