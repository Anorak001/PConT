import os
import json
import subprocess

# ------------------------------------------------------
# Define the command to call the scraper script
command = "python /path/to/other_script.py"

# Call the other script using subprocess.Popen()
subprocess.call(command, shell=True)

# ----------------------------------------------------
# Path to config file
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

# Function to extract IP from proxy string
def extract_ip(proxy):
    # Split on "://" to remove protocol and split again on ":" to remove the port
    return proxy.split("://")[-1].split(":")[0]

# Function to get user configuration
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

# Function to check only the required number of proxies
def check_required_proxies(proxies, required_length):
    online_proxies = []
    
    for proxy in proxies:
        # Stop checking once we've found enough active proxies
        if len(online_proxies) >= required_length:
            break
        
        # Remove newline character from the end of the line
        proxy = proxy.strip()

        # Extract IP from the proxy string
        ip = extract_ip(proxy)

        # Check if the proxy is online and add to the list
        if is_proxy_online(ip):
            online_proxies.append(proxy)

    return online_proxies

# Load proxies from the free_proxies.txt file
with open("free_proxies.txt") as f:
    proxies = f.readlines()

# Get user configuration
config = get_user_config()

# Check only the required number of proxies based on user input
selected_proxies = check_required_proxies(proxies, config["chain_length"])

# Output the selected proxies for the chain
print("Selected Proxies for the chain:")
for proxy in selected_proxies:
    print(proxy)
