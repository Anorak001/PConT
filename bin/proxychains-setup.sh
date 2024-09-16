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
#echo "Running setup scripts..."

# Navigate to the directory where the Python scripts are located
# Assuming that src and bin are in the same parent directory
PARENT_DIR="$(dirname "$(realpath "$0")")"
SRC_DIR="$PARENT_DIR/../src"
cd "$SRC_DIR" || exit

# Run each Python script in sequence
python3 intro.py

echo "Updating the proxylist from the API..."
python3 scraper.py



echo "Running Configuration Script with admin privileges..."
python3 config.py

echo "Setup completed."

