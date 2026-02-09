#!/bin/bash

# YAML file containing file paths
paths_yaml="file-paths.yaml"

# Check if the YAML file exists
if [ -f $paths_yaml ]; then
    echo "YAML file found!"
else
    echo "YAML file not found."
fi


gnb_exec=""
gnb_conf=""

# Use `yq` to parse the YAML file and extract the file paths
if ! gnb_exec=$(yq e ".ran.gnb.exec" $paths_yaml); then # gnb executable
    echo "Error: Failed to parse YAML file for gnb executable"
    exit 1
fi


print_usage() {
    echo "Usage: $0 -m mode -t type -b bandwidth [-d device] [-p place]"
    echo "  mode      - 1: simulation, 2: hardware"
    echo "  type      - 1: oai, 2: srsRAN"
    echo "  device    - 1: n310, 2: b210"
    echo "  place     - 1: host, 2: docker"
    echo "  bandwidth - 40: 40MHz, 60: 60MHz, 100: 100MHz"
}

# Parse arguments using getopts
while getopts ":m:t:b:d:p:h" opt; do
    case $opt in
        m)
            mode=$OPTARG
            ;;
        t)
            type=$OPTARG
            ;;
        b)
            bandwidth=$OPTARG
            ;;
        d)
            device=$OPTARG
            ;;
        p)
            place=$OPTARG
            ;;
        h)
            print_usage
            exit 0
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

# # Check if required arguments are provided
# if [ -z "$mode" ] || [ -z "$bandwidth" ] || [ -z "$place" ]; then
#     print_usage
#     exit 1
# fi


# Map mode, bandwidth, and place to respective configs
infer_str=""
case "$type" in
    1)
        infer_str=".ran.gnb.oai"
        ;;
    2)
        infer_str=".ran.gnb.srsRAN"
        ;;
    *)
        echo "Invalid type: $type. Use 1 for oai or 2 for srsRAN."
        print_usage
        exit 1
        ;;
esac

infer_str_conf=$infer_str".config"
infer_str_exec=$infer_str".exec"
arg_str=""
case "$mode" in
    1)
        infer_str_conf+=".simulation"
        arg_str+="--rfsim --rfsimulator.options chanmod --rfsimulator.serveraddr server --gNBs.[0].min_rxtxtime 6 "
        # arg_str+="--rfsim -E --rfsimulator.options chanmod --rfsimulator.serveraddr server --gNBs.[0].min_rxtxtime 6 "
        case "$place" in
            1)
                infer_str_conf+=".host"
                ;;
            2)
                infer_str_conf+=".docker"
                ;;
            *)
                echo "Invalid place: $place. Use 1 for host or 2 for docker."
                print_usage
                exit 1
                ;;
        esac
        ;;
    2)
        infer_str_conf+=".hardware"
        case "$device" in
            1)
                infer_str_conf+=".n310"
                ;;
            2)
                infer_str_conf+=".b210"
                ;;
            *)
                echo "Invalid place: $place. Use 1 for host or 2 for docker."
                print_usage
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Invalid mode: $mode. Use 1 for simulation or 2 for hardware."
        print_usage
        exit 1
        ;;
esac



case "$bandwidth" in
    40)
        infer_str_conf+=".40MHz"
        ;;
    60)
        infer_str_conf+=".60MHz"
        ;;
    100)
        infer_str_conf+=".100MHz"
        ;;
    *)
        echo "Invalid bandwidth: $bandwidth. Use 40, 60, or 100."
        print_usage
        exit 1
        ;;
esac

echo "Inferred config: $infer_str_conf"
echo "Inferred exec: $infer_str_exec"   

if ! gnb_conf=$(yq e $infer_str_conf $paths_yaml); then # gnb config
    echo "Error: Failed to parse YAML file for gnb config"
    exit 1
fi

if ! gnb_exec=$(yq e $infer_str_exec $paths_yaml); then # gnb executable
    echo "Error: Failed to parse YAML file for gnb executable"
    exit 1
fi

# Run the gnb executable
if [ "$type" = 1 ]; then
    sudo "$gnb_exec" -O "$gnb_conf" $arg_str
else
    sudo "$gnb_exec" -c "$gnb_conf"
fi


