import os
import sys
import subprocess
import time

# Configuration file paths
proxychains_conf_path = '/etc/proxychains.conf'
proxychains4_conf_path = '/etc/proxychains4.conf'

# Chains mapping
chains = {
    1: "strict_chain",
    2: "random_chain",
    3: "dynamic_chain",
    4: "round_robin_chain"
}

def is_proxy_online(ip):
    """Check if the proxy IP is online by pinging it with a timeout."""
    try:
        # Use subprocess to run ping with a 20-second timeout and suppress output
        result = subprocess.run(["ping", "-c", "1", "-W", "03", ip],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception as e:
        print(f"Error pinging {ip}: {e}", file=sys.stderr)
        return False

def extract_ip(proxy):
    """Extract IP from proxy string."""
    return proxy.split("://")[-1].split(":")[0]

def extract_protocol_port(proxy):
    """Extract protocol, IP, and port from proxy string."""
    protocol = proxy.split("://")[0]
    ip_port = proxy.split("://")[-1]
    ip = ip_port.split(":")[0]
    port = ip_port.split(":")[1]
    return protocol, ip, port

def get_user_config():
    """Get user configuration, including chain type and length."""
    print("Select the chain type:")
    print("1. Strict Chain")
    print("2. Random Chain")
    print("3. Dynamic Chain")
    print("4. Round-Robin Chain")
    
    try:
        choice = int(input("Enter the number corresponding to your choice: "))
        if choice not in chains:
            raise ValueError("Invalid choice")
    except ValueError as e:
        print(f"Invalid input: {e}. Using default 'Strict Chain'.")
        choice = 1  # Default to strict_chain

    chain_type = chains[choice]

    try:
        chain_length = int(input("Enter the length of the chain (0-25): "))
        if chain_length < 0 or chain_length > 25:
            raise ValueError("Chain length out of range")
    except ValueError as e:
        print(f"Invalid input: {e}. Using default length of 10.")
        chain_length = 10  # Default length

    return {
        "chain": chain_type,
        "chain_length": chain_length
    }

def print_progress_bar(iteration, total, length=50):
    """Print a simple text-based progress bar."""
    progress = (iteration / total) * 100
    filled_length = int(length * iteration // total)
    bar = '#' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {progress:.1f}% Complete')
    sys.stdout.flush()

def check_required_proxies(proxies, required_length):
    """Check only the required number of proxies with a custom progress bar."""
    online_proxies = []
    
    # Track progress
    print("Checking proxies:")
    
    for i, proxy in enumerate(proxies):
        if len(online_proxies) >= required_length:
            break

        proxy = proxy.strip()  # Remove newline character
        ip = extract_ip(proxy)

        # Display proxy status
        if is_proxy_online(ip):
            print(f"\nProxy {proxy} online!")
            online_proxies.append(proxy)
        else:
            print(f"\nProxy {proxy} down, skipping...")

        # Print progress bar
        print_progress_bar(len(online_proxies), required_length)
        time.sleep(0.1)  # Small delay to make progress visible

    # Complete the progress bar
    print('\n' + ' ' * 80)  # Clear the line after progress bar
    return online_proxies

def write_to_proxychains_conf(chain_type, proxies):
    """Write the selected chain and proxies to proxychains.conf and proxychains4.conf."""
    try:
        with open(proxychains_conf_path, 'w') as f:
            f.write(f"{chain_type}\n\n")
            f.write("[ProxyList]\n")
            
            for proxy in proxies:
                protocol, ip, port = extract_protocol_port(proxy)
                f.write(f"{protocol} {ip} {port}\n")
    except IOError as e:
        print(f"Error writing to {proxychains_conf_path}: {e}", file=sys.stderr)
    
    try:
        with open(proxychains4_conf_path, 'w') as f:
            f.write(f"{chain_type}\n\n")
            f.write("[ProxyList]\n")
            
            for proxy in proxies:
                protocol, ip, port = extract_protocol_port(proxy)
                f.write(f"{protocol} {ip} {port}\n")
    except IOError as e:
        print(f"Error writing to {proxychains4_conf_path}: {e}", file=sys.stderr)

def main():
    # Load proxies from free_proxies.txt
    try:
        with open("free_proxies.txt") as f:
            proxies = f.readlines()
    except FileNotFoundError:
        print("File 'free_proxies.txt' not found.", file=sys.stderr)
        return

    # Get user configuration
    config = get_user_config()

    # Check and select required number of proxies
    selected_proxies = check_required_proxies(proxies, config["chain_length"])

    # Write the configuration to proxychains.conf and proxychains4.conf
    write_to_proxychains_conf(config["chain"], selected_proxies)
    print(" ")
    print("Proxy setup is successful!")
    print("To use proxychains, run your commands with proxychains like this:")
 
    print("  proxychains <command>")
       print(" ")
    print("For example, to run curl through proxychains:")
    print("  proxychains curl http://example.com")
    print(" ")

if __name__ == "__main__":
    main()

