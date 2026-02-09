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
if ! ric_exec=$(yq e ".ran.ric.exec" $paths_yaml); then # docker compose file for basic core with slicing
    echo "Error: Failed to parse YAML file for ric executable"
    exit 1
fi

# Run the RIC executable
$ric_exec