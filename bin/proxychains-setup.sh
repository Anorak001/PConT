#!/usr/bin/bash

# Function to run commands with sudo
run_with_sudo() {
    if [ "$(id -u)" -ne "0" ]; then
        echo "This script requires root privileges. Attempting to elevate with sudo..."
        sudo "$0" "$@"
        exit
    fi
}

# Run the function to check and request sudo
run_with_sudo "$@"

# Run setup scripts
echo "Running setup scripts..."

# Example setup scripts
# Adjust the paths and commands as needed
#/bin/proxychains-start some-command
#/bin/proxychains-stop
#/bin/proxychains-help

# the main Python script
echo "Running main.py with admin privileges..."
python3 Pcont/src/main.py

echo "Setup completed."

