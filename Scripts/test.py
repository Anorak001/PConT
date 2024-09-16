import os
import json
import subprocess

# ------------------------------------------------------
# Define the command to call the scraper script
command = "python /path/to/other_script.py"

# Call the other script using subprocess.Popen()
subprocess.call(command, shell=True)

# ----------------------------------------------------
# path to config file
config_file = "/etc/proxyhains.conf"

# Define the chain options
chains = {
    "strict": "Strict Chain",
    "random": "Random Chain",
    "dynamic": "Dynamic Chain"
}

# Check if the proxy is up
def is_proxy_online(ip):
    # Send ping command and wait for response
    response = os.system("ping -c 1 {}".format(ip))
    # 0==success and -1==fail
    return response == 0

def get_user_config():
    # Read config file content if it exists
    try:
        with open(config_file) as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    chain = input("Enter the chain type (strict, random, dynamic): ")
    chain_length = int(input("Enter the length of the chain (0-25): "))

    # Update config with user inputs
    config["chain"] = chain
    config["chain_length"] = chain_length

    return config

# Function to strip out protocol and port
def extract_ip(proxy):
    # Split on "://" to remove protocol and split again on ":" to remove the port
    return proxy.split("://")[-1].split(":")[0]

# Function to build the proxy chain
def build_proxy_chain(online_proxies, chain_length):
    # Select the first 'chain_length' proxies from the list
    return online_proxies[:chain_length]

# Load proxies from the free_proxies.txt file
with open("free_proxies.txt") as f:
    proxies = f.readlines()

# Function to check proxies and build the chain based on user's configuration
def check_proxies_and_build_chain(proxies, config):
    online_proxies = []
    offline_proxies = []

    # Only check proxies and build the chain after user input
    for proxy in proxies:
        # Remove newline character from the end of the line
        proxy = proxy.strip()

        # Extract IP from the proxy string
        ip = extract_ip(proxy)

        # Check if the proxy is online and add to the appropriate list
        if is_proxy_online(ip):
            online_proxies.append(proxy)
        else:
            offline_proxies.append(proxy)

    # Build the proxy chain based on the online proxies and chain length
    selected_proxies = build_proxy_chain(online_proxies, config["chain_length"])

    return selected_proxies

# Get user configuration
config = get_user_config()

# Check proxies and build the chain after user selects configuration
selected_proxies = check_proxies_and_build_chain(proxies, config)

print("Selected Proxies for the chain:")
for proxy in selected_proxies:
    print(proxy)
