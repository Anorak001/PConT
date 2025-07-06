import os
import sys
import subprocess
import time
import json
import socket
import threading
import requests
import random
import argparse
import ipaddress
from datetime import datetime

# Configuration file paths 
proxychains_conf_path = '/etc/proxychains.conf'
proxychains4_conf_path = '/etc/proxychains4.conf'
# Create a directory for PConT in user's home directory
pcont_dir = os.path.expanduser('~/.pcont')
os.makedirs(pcont_dir, exist_ok=True)
pcont_db_path = os.path.join(pcont_dir, 'proxy_db.json')
pcont_config_path = os.path.join(pcont_dir, 'config.json')

# Chains mapping
chains = {
    1: "strict_chain",
    2: "random_chain",
    3: "dynamic_chain",
    4: "round_robin_chain"
}

# Default configuration
default_config = {
    "chain": "strict_chain",
    "chain_length": 10,
    "preferred_types": ["http", "socks4", "socks5"],
    "auto_rotate": False,
    "rotation_interval_minutes": 60,
    "max_ping_time": 1000,  # milliseconds
    "timeout": 10,
    "country_filter": "all",
    "anonymity_level": "all"  # options: all, anonymous, elite
}

def load_user_config():
    """Load configuration from file or create with defaults"""
    if os.path.exists(pcont_config_path):
        try:
            with open(pcont_config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading config file. Using defaults.")
            return default_config
    else:
        # Save default config if no config exists
        save_user_config(default_config)
        return default_config

def save_user_config(config):
    """Save configuration to file"""
    try:
        with open(pcont_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}", file=sys.stderr)
        return False

def get_proxy_speed(proxy, timeout=5):
    """Test proxy speed and return latency in milliseconds"""
    protocol, ip, port = extract_protocol_port(proxy)
    
    start_time = time.time()
    try:
        if protocol in ["http", "https"]:
            # HTTP proxy test
            proxies = {
                "http": f"{protocol}://{ip}:{port}",
                "https": f"{protocol}://{ip}:{port}"
            }
            response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
            if response.status_code == 200:
                end_time = time.time()
                return int((end_time - start_time) * 1000)  # Convert to ms
        else:
            # SOCKS proxy test with TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, int(port)))
            sock.close()
            end_time = time.time()
            return int((end_time - start_time) * 1000)  # Convert to ms
    except Exception:
        return float('inf')  # Indicate timeout or error
    
    return float('inf')  # Default to infinity if test fails

def is_proxy_online(ip, timeout=3):
    """Check if the proxy IP is online by pinging it with a timeout."""
    try:
        # Use subprocess to run ping with a timeout and suppress output
        result = subprocess.run(["ping", "-c", "1", "-W", str(timeout), ip],
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

def get_proxy_details(ip):
    """Get country and other details about a proxy IP."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=country,countryCode,city,isp,org", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data
        return None
    except Exception:
        return None

def test_proxy_connection(proxy, timeout=5):
    """Test if a proxy can successfully connect to the internet."""
    protocol, ip, port = extract_protocol_port(proxy)
    
    try:
        if protocol in ["http", "https"]:
            proxies = {
                "http": f"{protocol}://{ip}:{port}",
                "https": f"{protocol}://{ip}:{port}"
            }
            response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
            return response.status_code == 200
        elif protocol in ["socks4", "socks5"]:
            # We already tested connectivity with is_proxy_online or get_proxy_speed
            return True
        return False
    except Exception:
        return False

def update_proxy_database(proxies):
    """Update the proxy database with new information"""
    db = {}
    if os.path.exists(pcont_db_path):
        try:
            with open(pcont_db_path, 'r') as f:
                db = json.load(f)
        except json.JSONDecodeError:
            print("Error reading proxy database. Creating new one.")
    
    # Process each proxy
    for proxy in proxies:
        proxy = proxy.strip()
        if not proxy:
            continue
            
        protocol, ip, port = extract_protocol_port(proxy)
        
        # Skip if invalid IP
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            continue
            
        # Create or update entry
        if proxy not in db:
            db[proxy] = {
                "first_seen": datetime.now().isoformat(),
                "last_checked": datetime.now().isoformat(),
                "protocol": protocol,
                "ip": ip,
                "port": port,
                "online_count": 0,
                "offline_count": 0,
                "speed_history": [],
                "country": None,
                "isp": None
            }
        
        # Update last checked time
        db[proxy]["last_checked"] = datetime.now().isoformat()
        
        # Check if online and update status
        if is_proxy_online(ip):
            db[proxy]["online_count"] += 1
            
            # Get speed if it's online
            speed = get_proxy_speed(proxy)
            if speed < float('inf'):
                db[proxy]["speed_history"].append(speed)
                # Keep only last 5 speed tests
                if len(db[proxy]["speed_history"]) > 5:
                    db[proxy]["speed_history"] = db[proxy]["speed_history"][-5:]
            
            # Get country info if we don't have it yet
            if db[proxy]["country"] is None:
                details = get_proxy_details(ip)
                if details:
                    db[proxy]["country"] = details.get("country")
                    db[proxy]["countryCode"] = details.get("countryCode")
                    db[proxy]["city"] = details.get("city")
                    db[proxy]["isp"] = details.get("isp")
        else:
            db[proxy]["offline_count"] += 1
    
    # Save the updated database
    try:
        with open(pcont_db_path, 'w') as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"Error saving proxy database: {e}", file=sys.stderr)

def filter_proxies(proxies, config):
    """Filter proxies based on configuration"""
    filtered = []
    
    for proxy in proxies:
        proxy = proxy.strip()
        if not proxy:
            continue
            
        try:
            protocol, ip, port = extract_protocol_port(proxy)
            
            # Skip if protocol not in preferred types
            if protocol not in config["preferred_types"]:
                continue
                
            # Skip if IP is invalid
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                continue
                
            # Check if it's online
            if not is_proxy_online(ip):
                continue
                
            # Check speed if max_ping_time is set
            if config.get("max_ping_time"):
                speed = get_proxy_speed(proxy)
                if speed >= config["max_ping_time"]:
                    continue
                    
            # Add country filtering if database exists and country filter is set
            if config.get("country_filter") != "all" and os.path.exists(pcont_db_path):
                try:
                    with open(pcont_db_path, 'r') as f:
                        db = json.load(f)
                    
                    if proxy in db and db[proxy].get("countryCode"):
                        if db[proxy]["countryCode"] != config["country_filter"]:
                            continue
                except Exception:
                    pass  # If we can't check country, don't filter
            
            # Add proxy to filtered list
            filtered.append(proxy)
            
        except Exception as e:
            print(f"Error processing proxy {proxy}: {e}", file=sys.stderr)
    
    return filtered

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
        choice = 1  # Defaults to strict_chain

    chain_type = chains[choice]

    try:
        chain_length = int(input("Enter the length of the chain (0-25): "))
        if chain_length < 0 or chain_length > 25:
            raise ValueError("Chain length out of range")
    except ValueError as e:
        print(f"Invalid input: {e}. Using default length of 10.")
        chain_length = 10  # Default length
        
    # Get proxy type preferences
    print("\nSelect proxy types to include:")
    print("1. HTTP")
    print("2. SOCKS4")
    print("3. SOCKS5")
    print("4. All Types")
    
    try:
        type_choice = int(input("Enter your choice (1-4): "))
        if type_choice not in [1, 2, 3, 4]:
            raise ValueError("Invalid choice")
    except ValueError as e:
        print(f"Invalid input: {e}. Using all proxy types.")
        type_choice = 4
        
    preferred_types = []
    if type_choice == 1 or type_choice == 4:
        preferred_types.append("http")
    if type_choice == 2 or type_choice == 4:
        preferred_types.append("socks4")
    if type_choice == 3 or type_choice == 4:
        preferred_types.append("socks5")
        
    # Ask about auto-rotation
    try:
        auto_rotate = input("\nEnable automatic proxy rotation? (y/n): ").lower() == 'y'
        
        rotation_interval = 60  # Default 60 minutes
        if auto_rotate:
            try:
                rotation_interval = int(input("Enter rotation interval in minutes (default: 60): "))
                if rotation_interval < 1:
                    raise ValueError("Interval must be at least 1 minute")
            except ValueError as e:
                print(f"Invalid input: {e}. Using default interval of 60 minutes.")
                rotation_interval = 60
    except Exception:
        auto_rotate = False
        rotation_interval = 60
        
    # Ask about max ping time
    try:
        use_speed_filter = input("\nFilter proxies by speed? (y/n): ").lower() == 'y'
        
        max_ping_time = 1000  # Default 1000ms (1 second)
        if use_speed_filter:
            try:
                max_ping_time = int(input("Enter maximum ping time in milliseconds (default: 1000): "))
                if max_ping_time < 1:
                    raise ValueError("Ping time must be positive")
            except ValueError as e:
                print(f"Invalid input: {e}. Using default of 1000ms.")
                max_ping_time = 1000
    except Exception:
        use_speed_filter = False
        max_ping_time = None

    # Create and return the config
    config = {
        "chain": chain_type,
        "chain_length": chain_length,
        "preferred_types": preferred_types,
        "auto_rotate": auto_rotate,
        "rotation_interval_minutes": rotation_interval,
        "max_ping_time": max_ping_time if use_speed_filter else None
    }
    
    # Save the config
    save_user_config(config)
    
    return config

def print_progress_bar(iteration, total, length=50):
    """Print a simple text-based progress bar."""
    progress = (iteration / total) * 100
    filled_length = int(length * iteration // total)
    bar = '#' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {progress:.1f}% Complete')
    sys.stdout.flush()

def check_required_proxies(proxies, required_length, config=None):
    """Check only the required number of proxies with a custom progress bar."""
    if config is None:
        config = load_user_config()
        
    # First update the proxy database with all proxies
    update_proxy_database(proxies)
    
    # Then filter the proxies based on configuration
    filtered_proxies = filter_proxies(proxies, config)
    
    # Sort by speed if max_ping_time is set
    if config.get("max_ping_time"):
        proxy_speeds = []
        for proxy in filtered_proxies:
            speed = get_proxy_speed(proxy)
            if speed < float('inf'):
                proxy_speeds.append((proxy, speed))
                
        # Sort by speed (faster first)
        proxy_speeds.sort(key=lambda x: x[1])
        
        # Extract just the proxies
        filtered_proxies = [p[0] for p in proxy_speeds]
    
    # Take only the required number
    online_proxies = []
    
    print("Checking proxies:")
    
    for i, proxy in enumerate(filtered_proxies):
        if len(online_proxies) >= required_length:
            break

        proxy = proxy.strip()  # Remove newline character
        if not proxy:
            continue
            
        protocol, ip, port = extract_protocol_port(proxy)

        # Display proxy status
        if is_proxy_online(ip) and test_proxy_connection(proxy):
            # Get country information if available
            country_info = ""
            try:
                with open(pcont_db_path, 'r') as f:
                    db = json.load(f)
                if proxy in db and db[proxy].get("country"):
                    country_info = f" ({db[proxy]['country']})"
            except Exception:
                pass
                
            print(f"\nProxy {proxy}{country_info} online!")
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
    # First create backup of existing files if they exist
    for path in [proxychains_conf_path, proxychains4_conf_path]:
        if os.path.exists(path):
            try:
                backup_path = f"{path}.backup.{int(time.time())}"
                with open(path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                print(f"Created backup at {backup_path}")
            except Exception as e:
                print(f"Warning: Failed to create backup of {path}: {e}", file=sys.stderr)
    
    # Write the new configuration
    try:
        with open(proxychains_conf_path, 'w') as f:
            # Write basic config
            f.write(f"{chain_type}\n\n")
            f.write("# PConT automatically generated configuration\n")
            f.write("# Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            f.write("# Configuration options\n")
            f.write("tcp_read_time_out 15000\n")
            f.write("tcp_connect_time_out 8000\n")
            f.write("remote_dns_subnet 224\n")
            f.write("proxy_dns\n\n")
            
            # Write proxy list
            f.write("[ProxyList]\n")
            
            for proxy in proxies:
                protocol, ip, port = extract_protocol_port(proxy)
                f.write(f"{protocol} {ip} {port}\n")
    except IOError as e:
        print(f"Error writing to {proxychains_conf_path}: {e}", file=sys.stderr)
    
    try:
        with open(proxychains4_conf_path, 'w') as f:
            # Write basic config
            f.write(f"{chain_type}\n\n")
            f.write("# PConT automatically generated configuration\n")
            f.write("# Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            f.write("# Configuration options\n")
            f.write("tcp_read_time_out 15000\n")
            f.write("tcp_connect_time_out 8000\n")
            f.write("remote_dns_subnet 224\n")
            f.write("proxy_dns\n\n")
            
            # Write proxy list
            f.write("[ProxyList]\n")
            
            for proxy in proxies:
                protocol, ip, port = extract_protocol_port(proxy)
                f.write(f"{protocol} {ip} {port}\n")
    except IOError as e:
        print(f"Error writing to {proxychains4_conf_path}: {e}", file=sys.stderr)

def setup_rotation_daemon(config):
    """Set up a cron job to rotate proxies automatically"""
    if not config.get("auto_rotate"):
        return
        
    interval = config.get("rotation_interval_minutes", 60)
    
    # Create a rotation script
    rotation_script_path = os.path.join(pcont_dir, "rotate_proxies.sh")
    try:
        with open(rotation_script_path, 'w') as f:
            f.write("#!/bin/bash\n\n")
            f.write(f"# PConT proxy rotation script\n")
            f.write(f"# Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Get the path to the current script's directory
            f.write('SCRIPT_DIR="$(dirname "$(realpath "$0")")"\n')
            f.write('PARENT_DIR="$(dirname "$SCRIPT_DIR")"\n\n')
            
            # Call the setup script which will update the proxies
            f.write('# Run the setup script to update proxies\n')
            f.write('cd "$PARENT_DIR/bin" && ./proxychains-setup.sh\n')
            
        # Make the script executable
        os.chmod(rotation_script_path, 0o755)
        
        # Add to crontab
        cron_command = f"*/{interval} * * * * {rotation_script_path}"
        
        # Check if entry already exists
        try:
            crontab_output = subprocess.check_output(["crontab", "-l"], stderr=subprocess.DEVNULL).decode()
        except subprocess.CalledProcessError:
            crontab_output = ""
            
        if rotation_script_path not in crontab_output:
            # Add the new cron job
            new_crontab = crontab_output.strip() + "\n" + cron_command + "\n"
            subprocess.run(["bash", "-c", f'echo "{new_crontab}" | crontab -'])
            print(f"Set up automatic proxy rotation every {interval} minutes")
        
    except Exception as e:
        print(f"Failed to set up rotation daemon: {e}", file=sys.stderr)

def parse_args():
    """Parse command-line arguments for non-interactive mode"""
    parser = argparse.ArgumentParser(description='PConT - Proxy Configuration Tool')
    parser.add_argument('--chain-type', type=int, choices=[1, 2, 3, 4],
                      help='Chain type: 1=strict, 2=random, 3=dynamic, 4=round-robin')
    parser.add_argument('--chain-length', type=int,
                      help='Length of the proxy chain (0-25)')
    parser.add_argument('--proxy-types', 
                      help='Comma-separated proxy types to use (http,socks4,socks5)')
    parser.add_argument('--auto-rotate', action='store_true',
                      help='Enable automatic proxy rotation')
    parser.add_argument('--rotation-interval', type=int,
                      help='Proxy rotation interval in minutes')
    parser.add_argument('--max-ping', type=int,
                      help='Maximum ping time in milliseconds')
    parser.add_argument('--non-interactive', action='store_true',
                      help='Run in non-interactive mode using args or config file')
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Check if we're in non-interactive mode
    if args.non_interactive:
        # Load existing config as base
        config = load_user_config()
        
        # Update with command-line args if provided
        if args.chain_type:
            config["chain"] = chains[args.chain_type]
        if args.chain_length is not None:
            config["chain_length"] = max(0, min(25, args.chain_length))
        if args.proxy_types:
            config["preferred_types"] = args.proxy_types.split(',')
        if args.auto_rotate:
            config["auto_rotate"] = True
        if args.rotation_interval:
            config["rotation_interval_minutes"] = args.rotation_interval
        if args.max_ping:
            config["max_ping_time"] = args.max_ping
            
        # Save the updated config
        save_user_config(config)
    else:
        # Get user configuration interactively
        config = get_user_config()

    # Load proxies from free_proxies.txt
    try:
        with open("free_proxies.txt") as f:
            proxies = f.readlines()
    except FileNotFoundError:
        print("File 'free_proxies.txt' not found.", file=sys.stderr)
        return

    # Check and select required number of proxies
    selected_proxies = check_required_proxies(proxies, config["chain_length"], config)

    # Write the configuration to proxychains.conf and proxychains4.conf
    write_to_proxychains_conf(config["chain"], selected_proxies)
    
    # Set up rotation if enabled
    setup_rotation_daemon(config)
    
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

