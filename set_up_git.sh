#!/bin/bash

# Get the directory where the script is located
CWD="$(dirname "$(readlink -f "$0")")"
CONFIG_FILE="$CWD/.git/config"

# Check if the config file exists and contains [include]
if [ -f "$CONFIG_FILE" ] && grep -q "\[include\]" "$CONFIG_FILE"; then
    echo "Git config already set up"
    exit 1
fi

# Append the include configuration
cat >> "$CONFIG_FILE" << 'EOL'

[include]
path = ../.gitconfig