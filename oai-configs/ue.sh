#!/bin/bash

# YAML file containing file paths
paths_yaml="file-paths.yaml"

# Check if the YAML file exists
if [ -f $paths_yaml ]; then
    echo "YAML file found!"
else
    echo "YAML file not found."
fi

ue_exec=""
multi_ue_sh=""
ue_conf=""

# Use `yq` to parse the YAML file and extract the file paths
declare -A paths=(
    ["ue_exec"]=".ran.ue.exec"
    ["multi_ue_sh"]=".ran.ue.multi-ue"
)
for key in "${!paths[@]}"; do
    if ! value=$(yq e "${paths[$key]}" $paths_yaml); then
        echo "Error: Failed to parse YAML for key $key"
        exit 1
    fi
    declare "$key"="$value"
done

# Usage instructions
print_usage() {
    echo "Usage: $0 -m <mode> -b <bandwidth> -p <place> -i <ue_id>"
    echo "  -m      - 1: simulation, 2: hardware"
    echo "  -b      - 40: 40MHz, 60: 60MHz, 100: 100MHz"
    echo "  -p      - 1: host, 2: docker"
    echo "  -i      - UE ID (integer) Eg: 1"
}

# Parse arguments using getopts
while getopts ":m:b:p:i:" opt; do
  case $opt in
    m)
      mode=$OPTARG
      ;;
    b)
      bandwidth=$OPTARG
      ;;
    p)
      place=$OPTARG
      ;;
    i)
      ue_id=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      print_usage
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      print_usage
      exit 1
      ;;
  esac
done

# Check if required arguments are provided
if [ -z "$mode" ] || [ -z "$bandwidth" ] || [ -z "$place" ] || [ -z "$ue_id" ]; then
    print_usage
    exit 1
fi

# Map mode, bandwidth, place and ue_id to respective configs
infer_str=".ran.ue.config"
arg_str=""
case "$mode" in
    1)
        infer_str="$infer_str.simulation"
        BASE_IP=$((200+ue_id))
        arg_str+="--rfsim --rfsimulator.options chanmod --rfsimulator.serveraddr 10.$BASE_IP.1.100"
        # arg_str+="--sa -E --rfsim --rfsimulator.options chanmod --rfsimulator.serveraddr 10.$BASE_IP.1.100"
        ;;
    2)
        infer_str="$infer_str.hardware"
        ;;
    *)
        echo "Invalid mode: $mode"
        print_usage
        exit 1
        ;;
esac

case "$place" in
    1)
        infer_str="$infer_str.host"
        ;;
    2)
        infer_str="$infer_str.docker"
        ;;
    *)
        echo "Invalid place: $place"
        print_usage
        exit 1
        ;;
esac

infer_str="$infer_str.ue$ue_id"

prb=0
case "$bandwidth" in
    40)
        prb=106
        ;;
    60)
        prb=162
        ;;
    100)
        prb=273
        ;;
    *)
        echo "Invalid bandwidth: $bandwidth"
        print_usage
        exit 1
        ;;
esac

# Use `yq` to parse the YAML file and extract the file paths
if ! ue_conf=$(yq e "$infer_str" $paths_yaml); then # gnb executable
    echo "Error: Failed to parse YAML file for gnb config"
    exit 1
fi

# Create the namespace ue
sudo "$multi_ue_sh" -c "$ue_id"

# Run the UE executable
sudo ip netns exec ue"$ue_id" "$ue_exec" -O "$ue_conf" -r $prb --numerology 1 --band 78 -C 3619200000 $arg_str

# Delete the namespace ue
sudo "$multi_ue_sh" -d "$ue_id"