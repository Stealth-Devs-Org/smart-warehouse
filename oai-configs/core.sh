#!/bin/bash

# YAML file containing file paths
paths_yaml="file-paths.yaml"

# Check if the YAML file exists
if [ -f $paths_yaml ]; then
    echo "YAML file found!"
else
    echo "YAML file not found."
fi

# Use `yq` to parse the YAML file and extract the file paths
if ! dc_slice_basic_nrf=$(yq e ".core.docker-compose.slicing-basic-nrf" $paths_yaml); then # docker compose file for basic core with slicing
    echo "Error: Failed to parse YAML file for dc-slice-basic-nrf"
    exit 1
fi

# Usage instructions
print_usage() {
    echo "Usage: $0 [up|down]"
    echo "  up   - Start the Docker Compose services for the core network with slicing"
    echo "  down - Stop the Docker Compose services"
}

# Parse argument
if [ "$1" == "up" ]; then
    # docker compose up core with slice
    docker compose -f "$dc_slice_basic_nrf" up -d
elif [ "$1" == "down" ]; then
    # docker compose down core with slice
    docker compose -f "$dc_slice_basic_nrf" down
elif [ "$1" == "help" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    print_usage
    exit 0
elif [ "$1" == "" ]; then
    echo "No argument provided. Use 'up' or 'down'."
    print_usage
    exit 1
else
    echo "Invalid argument: $1. Use 'up' or 'down'."
    print_usage
    exit 1
fi