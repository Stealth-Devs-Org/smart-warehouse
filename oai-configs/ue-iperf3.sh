#!/bin/bash

# Usage instructions
print_usage() {
  echo "Usage: $0 <ue_id> [options]"
  echo "  <ue_id> - UE ID (integer) Eg: 1"
  echo "  [options] - Additional arguments for iperf3"
}

# Get the first argument
ueid=$1

# Check if ueid is provided
if [ -z "$ueid" ]; then
  echo "Error: UE ID is not provided."
  print_usage
  exit 1
fi

# Check if namespace exists
if ! sudo ip netns list | grep -q "ue$ueid"; then
  echo "Error: ue$ueid namespace does not exist."
  exit 1
fi

# Check if oaitun_ue1 interface exists
if ! sudo ip netns exec ue"$ueid" ip link show oaitun_ue1 > /dev/null 2>&1; then
  echo "Error: oaitun_ue1 interface does not exist."
  exit 1
fi

# Get IP address of oaitun_ue1 interface
ip_add=$(sudo ip netns exec ue"$ueid" ip -4 addr show oaitun_ue1 | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1)
echo "UE1 IP address: $ip_add"

# Get every argument after first as a string
arg_str=""
for arg in "${@:2}"; do
  arg_str+=" $arg"
done

# Run iperf3 server in the UE1 namespace with arguments
sudo ip netns exec ue"$ueid" iperf3 $arg_str