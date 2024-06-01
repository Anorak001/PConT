#!/bin/bash

# Update system and install proxychains
sudo apt update
sudo apt install -y proxychains

# Backup existing proxychains configuration
if [ -f /etc/proxychains.conf ]; then
    sudo cp /etc/proxychains.conf /etc/proxychains.conf.bak
fi

# Create new proxychains configuration
cat <<EOL | sudo tee /etc/proxychains.conf
# ProxyChains default configuration file

dynamic_chain

# Proxy DNS requests
proxy_dns

# Number of seconds to wait for a connection to the proxy.
timeout 5000

# Uncomment the following line to enable localnet exclusions
# localnet 127.0.0.0/255.0.0.0
# localnet 10.0.0.0/255.0.0.0
# localnet 172.16.0.0/255.240.0.0
# localnet 192.168.0.0/255.255.0.0

# The proxies list
# Format: [type] [IP] [port] [user] [pass]
# Types: http, socks4, socks5
[ProxyList]
# add your proxy servers here
# example:
# socks5 127.0.0.1 9050

# Example proxies
# socks4 192.168.57.1 1080
# http 192.168.57.2 8080
socks5 127.0.0.1 9050
EOL

echo "ProxyChains has been configured. Please edit /etc/proxychains.conf if you need to change proxy settings."

# Install and start TOR
sudo apt install -y tor
sudo systemctl start tor
sudo systemctl enable tor

echo "TOR has been installed and started. Use proxychains with any application to route through TOR."
