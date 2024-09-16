#!/bin/bash

# Define paths
CONFIG_FILE="/etc/proxychains.conf"
BACKUP_FILE="/etc/proxychains.conf.bak"
DEFAULT_CONFIG_CONTENT="# Default proxychains configuration\n# Empty or default settings\n"

# Function to reset proxychains configuration
reset_proxychains_config() {
    if [ -f "$BACKUP_FILE" ]; then
        echo "Restoring original proxychains configuration..."
        cp "$BACKUP_FILE" "$CONFIG_FILE"
        echo "Proxychains configuration restored."
    else
        echo "Backup configuration file not found."
        echo "Creating a default proxychains configuration file..."
        echo -e "$DEFAULT_CONFIG_CONTENT" > "$CONFIG_FILE"
        echo "Default proxychains configuration created."
    fi
}

# Function to reset network proxy settings
reset_network_settings() {
    echo "Resetting network proxy settings..."

    # For Linux systems, clear environment variables
    unset http_proxy
    unset https_proxy
    unset ftp_proxy

    # Optionally reset system-wide network proxy settings
    # For example, on Debian-based systems:
    # sudo gsettings reset-recursively org.gnome.system.proxy

    echo "Network proxy settings have been cleared."
}

# Main script execution
echo "Starting proxychains reset process..."

reset_proxychains_config
reset_network_settings

echo "Proxychains and network settings have been reset."
