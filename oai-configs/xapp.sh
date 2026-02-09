#!/bin/bash

# YAML file containing file paths
paths_yaml="file-paths.yaml"

# Check if the YAML file exists
if [ -f $paths_yaml ]; then
    echo "YAML file found!"
else
    echo "YAML file not found."
fi

# Usage instructions
print_usage() {
    echo "Usage: $0 <xapp>"
    echo "  xapp - xapp name"
    echo "  available xapps: [KPM-moni  RC-moni  RC-ctrl  Slice-ctrl  MAC-RLC-PDCP-GTP-moni]"
}

# Get first argument
if [ "$1" == "help" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    print_usage
    exit 0
elif [ "$1" == "" ]; then
    echo "No argument provided."
    print_usage
    exit 1
else
    xapp=$1
fi

# Get xapp path
infer_str=".ran.ric.xapp.$xapp"
if ! xapp_exec=$(yq e "$infer_str" $paths_yaml); then
    echo "Error: Failed to parse YAML file for xapp executable"
    print_usage
    exit 1
fi

# Run the xapp executable
$xapp_exec