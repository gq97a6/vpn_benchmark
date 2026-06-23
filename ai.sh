#!/bin/bash

# Example: excludes directory 'photos/cats' and specific file '.env'
EXCLUDE=(
    ".git"
    "ai.sh"
    "process-results"
    "LICENSE"
    "iso-guest/config/includes.chroot/etc/wireguard"
    "iso-guest/config/includes.chroot/etc/nebula"
    "iso-guest/config/includes.chroot/etc/openvpn"
    "iso-host/config/includes.chroot/root/benchmark/__pycache__"
)

TREE_PATTERN=$(printf '%s\n' "${EXCLUDE[@]}" | sed 's/\./\\./g' | paste -sd '|' -)

PRUNE_EXPR=""
for item in "${EXCLUDE[@]}"; do
    if [ -z "$PRUNE_EXPR" ]; then
        PRUNE_EXPR="-path ./$item"
    else
        PRUNE_EXPR="$PRUNE_EXPR -o -path ./$item"
    fi
done

echo "--- Project Tree ---"
tree -I "$TREE_PATTERN"

echo -e "\n--- File Contents ---"
find . \( $PRUNE_EXPR \) -prune -o -type f -print | while read -r file; do
    echo "FILE: $file"
    echo "------------------------------------------------------------------------"
    cat "$file"
    echo -e "\n------------------------------------------------------------------------\n"
done