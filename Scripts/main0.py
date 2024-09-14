import os
import json
import requests

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

#check if the proxy is up
def is_proxy_online(ip):
    # Send ping command and wait for response
    response = os.system("ping -c 1 {}".format(ip))

    # 0==sucecess and -1==fail
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





# Load proxies from the free_proxies.txt file
with open("free_proxies.txt") as f:
    proxies = f.readlines()

online_proxies = []
offline_proxies = []

for proxy in proxies:
    # Remove newline character from the end of the line
    proxy = proxy.strip()
    
    if is_proxy_online(proxy):
        online_proxies.append(proxy)
    else:
        offline_proxies.append(proxy)



config = get_user_config()
print("Selected Proxies:")
for proxy in online_proxies:
    print(proxy)