import os
import json
import subprocess

# ------------------------------------------------------
# Define the command to call the scraper script
command = "python /path/to/other_script.py"

# Call the other script using subprocess.Popen()
subprocess.call(command, shell=True)

# ----------------------------------------------------
# Path to proxychains.conf file
config_file = "/etc/proxychains.conf"

# Define the chain options
chains = {
    "strict": "strict_chain",
    "random": "random_chain",
    "dynamic": "dynamic_chain"
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

# Function to extract protocol and port from proxy string
def extract_protocol_port(proxy):
    protocol = proxy.split("://")[0]
    ip_port = proxy.split("://")[-1]
    ip = ip_port.split(":")[0]
    port = ip_port.split(":")[1]
    return protocol, ip, port

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

# Function to write the selected chain and proxies to proxychains.conf
def write_to_proxychains_conf(chain_type, proxies):
    with open(config_file, 'w') as f:
        # Write the chain type
        f.write(f"{chain_type}\n\n")
        f.write("[ProxyList]\n")
        
        # Write each proxy in the correct format
        for proxy in proxies:
            protocol, ip, port = extract_protocol_port(proxy)
            f.write(f"{protocol} {ip} {port}\n")

# Load proxies from the free_proxies.txt file
with open("free_proxies.txt") as f:
    proxies = f.readlines()

# Get user configuration
config = get_user_config()

# Check only the required number of proxies based on user input
selected_proxies = check_required_proxies(proxies, config["chain_length"])

# Write the configuration to the proxychains.conf file
write_to_proxychains_conf(chains[config["chain"]], selected_proxies)

print("Proxies written to proxychains.conf:")
for proxy in selected_proxies:
    print(proxy)
