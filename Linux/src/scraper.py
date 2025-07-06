import requests
import json
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
import random
import time

def get_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Proxy scraping script for PConT')
    parser.add_argument('--proxy-types', default='http,socks4,socks5', 
                      help='Comma-separated list of proxy types to fetch (http,socks4,socks5)')
    parser.add_argument('--country', default='all',
                      help='Country code to filter proxies (e.g., US, DE, all)')
    parser.add_argument('--timeout', type=int, default=10,
                      help='Maximum timeout in seconds for proxy requests')
    parser.add_argument('--limit', type=int, default=100,
                      help='Maximum number of proxies to fetch')
    parser.add_argument('--output', default='free_proxies.txt',
                      help='Output file name')
    return parser.parse_args()

def fetch_proxyscrape(proxy_types='http,socks4,socks5', country='all', timeout=10, limit=100):
    """Fetch proxies from proxyscrape.com"""
    base_url = f"https://api.proxyscrape.com/v3/free-proxy-list/get"
    
    params = {
        'request': 'displayproxies',
        'proxy_format': 'protocolipport',
        'format': 'text',
        'proxy_type': proxy_types,
        'timeout': timeout * 1000,  # Convert to milliseconds
        'country': country if country != 'all' else '',
        'limit': limit
    }
    
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200 and response.text.strip():
            return response.text.strip().split('\n')
        else:
            print(f"Error fetching from proxyscrape: {response.status_code}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Exception when fetching from proxyscrape: {e}", file=sys.stderr)
        return []

def fetch_geonode(proxy_types='http,socks4,socks5', country='all', limit=100):
    """Fetch proxies from geonode.com"""
    protocols = []
    if 'http' in proxy_types:
        protocols.extend(['http', 'https'])
    if 'socks4' in proxy_types:
        protocols.append('socks4')
    if 'socks5' in proxy_types:
        protocols.append('socks5')
    
    protocol_param = ','.join(protocols)
    country_param = country if country != 'all' else ''
    
    base_url = "https://proxylist.geonode.com/api/proxy-list"
    params = {
        'limit': limit,
        'page': 1,
        'sort_by': 'lastChecked',
        'sort_type': 'desc',
        'protocols': protocol_param
    }
    
    if country_param:
        params['country'] = country_param
    
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            proxies = []
            for proxy in data.get('data', []):
                protocol = proxy.get('protocols')[0] if proxy.get('protocols') else 'http'
                ip = proxy.get('ip')
                port = proxy.get('port')
                if ip and port:
                    proxies.append(f"{protocol}://{ip}:{port}")
            return proxies
        else:
            print(f"Error fetching from geonode: {response.status_code}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Exception when fetching from geonode: {e}", file=sys.stderr)
        return []

def fetch_all_proxies(args):
    """Fetch proxies from all sources"""
    all_proxies = []
    
    # Use ThreadPoolExecutor to fetch proxies in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit fetch tasks
        proxyscrape_future = executor.submit(
            fetch_proxyscrape, 
            args.proxy_types, 
            args.country, 
            args.timeout, 
            args.limit
        )
        
        geonode_future = executor.submit(
            fetch_geonode,
            args.proxy_types,
            args.country,
            args.limit
        )
        
        # Get results
        proxyscrape_proxies = proxyscrape_future.result()
        geonode_proxies = geonode_future.result()
        
        # Combine and deduplicate
        all_proxies = list(set(proxyscrape_proxies + geonode_proxies))
        
        # Shuffle to mix sources
        random.shuffle(all_proxies)
        
        # Limit the number if needed
        if args.limit and len(all_proxies) > args.limit:
            all_proxies = all_proxies[:args.limit]
    
    return all_proxies

def save_proxies(proxies, output_file):
    """Save proxies to file"""
    try:
        with open(output_file, 'w') as f:
            for proxy in proxies:
                if proxy.strip():
                    f.write(f"{proxy.strip()}\n")
        print(f"Successfully saved {len(proxies)} proxies to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving proxies to {output_file}: {e}", file=sys.stderr)
        return False

def main():
    """Main function"""
    args = get_args()
    
    print(f"Fetching proxies with types: {args.proxy_types}")
    if args.country != 'all':
        print(f"Filtering by country: {args.country}")
    
    proxies = fetch_all_proxies(args)
    
    if proxies:
        print(f"Found {len(proxies)} proxies")
        save_proxies(proxies, args.output)
    else:
        print("No proxies found!")
        # Create an empty file to avoid errors in downstream scripts
        with open(args.output, 'w') as f:
            pass

if __name__ == "__main__":
    main()
