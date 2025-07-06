#!/usr/bin/env python3
# filepath: /media/thestalrus/OS/Users/manth/Documents/GitHub/PConT/Linux/src/cli.py
import os
import sys
import argparse
import json
import time
import subprocess
from datetime import datetime

# Import our own modules
from config import (
    chains, load_user_config, save_user_config, 
    check_required_proxies, write_to_proxychains_conf,
    setup_rotation_daemon, pcont_dir, pcont_config_path
)

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='PConT - Proxy Configuration Tool (CLI)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Setup commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Configure command
    configure_parser = subparsers.add_parser('configure', help='Configure proxychains')
    configure_parser.add_argument('--chain-type', type=int, choices=[1, 2, 3, 4], default=1,
                               help='Chain type (1=strict, 2=random, 3=dynamic, 4=round-robin)')
    configure_parser.add_argument('--chain-length', type=int, default=10,
                               help='Length of the proxy chain (0-25)')
    configure_parser.add_argument('--proxy-types', default='http,socks4,socks5',
                               help='Comma-separated proxy types to use')
    configure_parser.add_argument('--auto-rotate', action='store_true',
                               help='Enable automatic proxy rotation')
    configure_parser.add_argument('--rotation-interval', type=int, default=60,
                               help='Proxy rotation interval in minutes')
    configure_parser.add_argument('--max-ping', type=int,
                               help='Maximum ping time in milliseconds')
    configure_parser.add_argument('--country', default='all',
                               help='Country code to filter proxies (e.g., US, DE)')
    configure_parser.add_argument('--proxy-file', default='free_proxies.txt',
                               help='File containing list of proxies')
    configure_parser.add_argument('--no-save', action='store_true',
                               help='Do not save configuration to file')
    
    # Update command for fetching new proxies
    update_parser = subparsers.add_parser('update', help='Update proxy list')
    update_parser.add_argument('--proxy-types', default='http,socks4,socks5',
                            help='Comma-separated proxy types to fetch')
    update_parser.add_argument('--country', default='all',
                            help='Country code to filter proxies (e.g., US, DE)')
    update_parser.add_argument('--limit', type=int, default=100,
                            help='Maximum number of proxies to fetch')
    update_parser.add_argument('--timeout', type=int, default=10,
                            help='Maximum timeout in seconds for proxy requests')
    update_parser.add_argument('--output', default='free_proxies.txt',
                            help='Output file name')
    
    # Status command to show current configuration
    status_parser = subparsers.add_parser('status', help='Show current configuration')
    status_parser.add_argument('--json', action='store_true',
                            help='Output in JSON format')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset proxychains configuration')
    reset_parser.add_argument('--defaults', action='store_true',
                           help='Also reset PConT configuration to defaults')
    
    return parser.parse_args()

def run_configure(args):
    """Run the configure command"""
    # Convert chain type to chain string
    chain_type = chains.get(args.chain_type, "strict_chain")
    
    # Parse proxy types
    proxy_types = args.proxy_types.split(',')
    
    # Create config
    config = {
        "chain": chain_type,
        "chain_length": args.chain_length,
        "preferred_types": proxy_types,
        "auto_rotate": args.auto_rotate,
        "rotation_interval_minutes": args.rotation_interval,
        "max_ping_time": args.max_ping,
        "country_filter": args.country
    }
    
    # Save config if not disabled
    if not args.no_save:
        save_user_config(config)
        print(f"Configuration saved to {pcont_config_path}")
    
    # Load proxies
    try:
        with open(args.proxy_file) as f:
            proxies = f.readlines()
        print(f"Loaded {len(proxies)} proxies from {args.proxy_file}")
    except FileNotFoundError:
        print(f"Error: File '{args.proxy_file}' not found.", file=sys.stderr)
        print("Run 'python3 cli.py update' to fetch proxies first.")
        return 1
    
    # Check and select required number of proxies
    selected_proxies = check_required_proxies(proxies, config["chain_length"], config)
    
    if not selected_proxies:
        print("Error: No suitable proxies found", file=sys.stderr)
        return 1
    
    # Write configuration
    try:
        write_to_proxychains_conf(config["chain"], selected_proxies)
        print("Configuration files written successfully")
    except Exception as e:
        print(f"Error writing configuration: {e}", file=sys.stderr)
        return 1
    
    # Set up rotation if enabled
    if config.get("auto_rotate"):
        try:
            setup_rotation_daemon(config)
            print(f"Automatic proxy rotation set up (every {config['rotation_interval_minutes']} minutes)")
        except Exception as e:
            print(f"Error setting up rotation: {e}", file=sys.stderr)
    
    print("\nProxy setup completed successfully!")
    print("To use proxychains, run your commands with proxychains like this:")
    print("  proxychains <command>")
    print("\nFor example, to run curl through proxychains:")
    print("  proxychains curl http://example.com")
    
    return 0

def run_update(args):
    """Run the update command to fetch new proxies"""
    # Import scraper functions
    try:
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from scraper import fetch_all_proxies, save_proxies
    except ImportError:
        print("Error: Could not import scraper module", file=sys.stderr)
        return 1
    
    # Create args object for fetch_all_proxies
    class ScraperArgs:
        def __init__(self, proxy_types, country, timeout, limit, output):
            self.proxy_types = proxy_types
            self.country = country
            self.timeout = timeout
            self.limit = limit
            self.output = output
    
    scraper_args = ScraperArgs(
        args.proxy_types,
        args.country,
        args.timeout,
        args.limit,
        args.output
    )
    
    print(f"Fetching proxies with types: {args.proxy_types}")
    if args.country != 'all':
        print(f"Filtering by country: {args.country}")
    
    # Fetch proxies
    proxies = fetch_all_proxies(scraper_args)
    
    if proxies:
        print(f"Found {len(proxies)} proxies")
        save_proxies(proxies, args.output)
        return 0
    else:
        print("No proxies found!")
        return 1

def run_status(args):
    """Show current configuration status"""
    # Load config
    config = load_user_config()
    
    if args.json:
        # Output as JSON
        print(json.dumps(config, indent=2))
    else:
        # Pretty print configuration
        print("Current PConT Configuration:")
        print("===========================")
        
        # Chain type
        chain_type = config.get("chain", "strict_chain")
        print(f"Chain Type: {chain_type}")
        
        # Chain length
        chain_length = config.get("chain_length", 10)
        print(f"Chain Length: {chain_length}")
        
        # Proxy types
        proxy_types = config.get("preferred_types", ["http", "socks4", "socks5"])
        print(f"Proxy Types: {', '.join(proxy_types)}")
        
        # Auto rotation
        auto_rotate = config.get("auto_rotate", False)
        if auto_rotate:
            interval = config.get("rotation_interval_minutes", 60)
            print(f"Auto Rotation: Enabled (every {interval} minutes)")
        else:
            print("Auto Rotation: Disabled")
        
        # Speed filtering
        max_ping = config.get("max_ping_time")
        if max_ping is not None:
            print(f"Speed Filtering: Enabled (max ping: {max_ping}ms)")
        else:
            print("Speed Filtering: Disabled")
        
        # Country filtering
        country = config.get("country_filter", "all")
        if country != "all":
            print(f"Country Filtering: {country}")
        else:
            print("Country Filtering: None (all countries)")
        
        print("\nProxychains Configuration Files:")
        print("===============================")
        
        # Check if proxychains.conf exists
        from config import proxychains_conf_path, proxychains4_conf_path
        
        if os.path.exists(proxychains_conf_path):
            print(f"- {proxychains_conf_path} (exists)")
        else:
            print(f"- {proxychains_conf_path} (not found)")
            
        if os.path.exists(proxychains4_conf_path):
            print(f"- {proxychains4_conf_path} (exists)")
        else:
            print(f"- {proxychains4_conf_path} (not found)")
    
    return 0

def run_reset(args):
    """Reset proxychains configuration"""
    # Import reset function
    try:
        # First check if the user has sufficient permissions
        if os.geteuid() != 0:
            print("Error: This command requires root privileges.", file=sys.stderr)
            print("Please run with sudo: sudo python3 cli.py reset", file=sys.stderr)
            return 1
        
        # Paths from config
        from config import proxychains_conf_path, proxychains4_conf_path
        
        # Reset proxychains.conf
        if os.path.exists(proxychains_conf_path):
            # Create backup
            backup_path = f"{proxychains_conf_path}.backup.{int(time.time())}"
            with open(proxychains_conf_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            print(f"Created backup at {backup_path}")
            
            # Write default config
            with open(proxychains_conf_path, 'w') as f:
                f.write("""# ProxyChains default configuration
# Reset by PConT on {date}

# This configuration uses the default chain
strict_chain

# Basic configuration
tcp_read_time_out 15000
tcp_connect_time_out 8000
remote_dns_subnet 224
proxy_dns

[ProxyList]
# Add your proxies here
# Format: <type> <ip> <port>
# Example: http 1.2.3.4 8080
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            print(f"Reset {proxychains_conf_path} to default configuration")
        
        # Reset proxychains4.conf
        if os.path.exists(proxychains4_conf_path):
            # Create backup
            backup_path = f"{proxychains4_conf_path}.backup.{int(time.time())}"
            with open(proxychains4_conf_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            print(f"Created backup at {backup_path}")
            
            # Write default config
            with open(proxychains4_conf_path, 'w') as f:
                f.write("""# ProxyChains4 default configuration
# Reset by PConT on {date}

# This configuration uses the default chain
strict_chain

# Basic configuration
tcp_read_time_out 15000
tcp_connect_time_out 8000
remote_dns_subnet 224
proxy_dns

[ProxyList]
# Add your proxies here
# Format: <type> <ip> <port>
# Example: http 1.2.3.4 8080
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            print(f"Reset {proxychains4_conf_path} to default configuration")
        
        # Reset PConT configuration if requested
        if args.defaults and os.path.exists(pcont_config_path):
            os.remove(pcont_config_path)
            print(f"Removed PConT configuration file: {pcont_config_path}")
            
            # Re-create with defaults
            from config import default_config, save_user_config
            save_user_config(default_config)
            print(f"Created new default configuration in {pcont_config_path}")
        
        # Remove cron job if it exists
        try:
            crontab_output = subprocess.check_output(["crontab", "-l"], stderr=subprocess.DEVNULL).decode()
            if "rotate_proxies.sh" in crontab_output:
                new_crontab = "\n".join([line for line in crontab_output.split("\n") 
                                        if "rotate_proxies.sh" not in line])
                subprocess.run(["bash", "-c", f'echo "{new_crontab}" | crontab -'])
                print("Removed proxy rotation from crontab")
        except:
            pass
        
        print("\nReset completed successfully")
        
    except Exception as e:
        print(f"Error during reset: {e}", file=sys.stderr)
        return 1
    
    return 0

def main():
    # Parse arguments
    args = parse_args()
    
    # Create the PConT directory if it doesn't exist
    os.makedirs(pcont_dir, exist_ok=True)
    
    # Execute the appropriate command
    if args.command == 'configure':
        return run_configure(args)
    elif args.command == 'update':
        return run_update(args)
    elif args.command == 'status':
        return run_status(args)
    elif args.command == 'reset':
        return run_reset(args)
    else:
        # No command specified, show help
        print("Error: No command specified", file=sys.stderr)
        print("Run 'python3 cli.py -h' for help", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
