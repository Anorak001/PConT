#!/usr/bin/bash

# Display PConT ASCII art
echo -e "\e[32m"
echo '██████╗  ██████╗ ██████╗ ███╗   ██╗████████╗'
echo '██╔══██╗██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝'
echo '██████╔╝██║     ██║   ██║██╔██╗ ██║   ██║   '
echo '██╔═══╝ ██║     ██║   ██║██║╚██╗██║   ██║   '
echo '██║     ╚██████╗╚██████╔╝██║ ╚████║   ██║   '
echo '╚═╝      ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   '
echo -e "\e[0m"

echo -e "\e[1m\e[32mPConT - Proxy Configuration Tool\e[0m"
echo -e "\e[1m\e[32mBy Anorak001\e[0m"
echo ""

# Display help information for PConT and proxychains
echo "PConT Commands:"
echo "==============="
echo "  proxychains-setup        Configure proxychains with GUI or CLI interfaces"
echo "  proxychains-reset        Reset proxychains configuration to defaults"
echo "  proxychains-help         Show this help message"
echo ""

echo "proxychains-setup Options:"
echo "========================="
echo "  -h, --help            Show help message and exit"
echo "  -g, --gui             Launch the GUI interface"
echo "  -c, --cli             Use the CLI interface with prompts"
echo "  -n, --non-interactive Configure using saved settings without prompts"
echo "  -u, --update          Update the proxy list before configuring"
echo "  -v, --validate        Validate proxies before configuring"
echo "  --chain=TYPE          Chain type (1=strict, 2=random, 3=dynamic, 4=round-robin)"
echo "  --length=N            Chain length (0-25)"
echo "  --types=LIST          Comma-separated proxy types (http,socks4,socks5)"
echo "  --country=CODE        Country code filter (e.g., US, DE, all)"
echo ""

echo "Proxychains Usage:"
echo "================="
echo "  proxychains [options] <command> [args...]"
echo ""
echo "  Options:"
echo "    -q                   Make proxychains quiet"
echo "    -f <config_file>     Use custom config file"
echo "    -h                   Show proxychains help"
echo ""

echo "Examples:"
echo "========="
echo "  proxychains-setup -g                  # Launch the GUI configurator"
echo "  proxychains-setup -u -v               # Update and validate proxies"
echo "  proxychains-setup -n                  # Configure using saved settings"
echo "  proxychains-setup --chain=2 --length=5 --types=socks4,socks5"
echo ""
echo "  proxychains curl http://example.com   # Run curl through the proxy chain"
echo "  proxychains firefox                   # Run Firefox through the proxy chain"
echo ""

echo "For more information, refer to the README.md or visit the GitHub repository."
