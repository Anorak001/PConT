#!/usr/bin/env python3
# filepath: /media/thestalrus/OS/Users/manth/Documents/GitHub/PConT/Linux/src/validator.py
import os
import sys
import time
import json
import socket
import threading
import concurrent.futures
import argparse
import requests
from datetime import datetime
import ipaddress

# Get proxy database path from config
try:
    from config import pcont_db_path, get_proxy_details, extract_protocol_port
except ImportError:
    pcont_db_path = os.path.expanduser('~/.pcont/proxy_db.json')
    
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

class ProxyValidator:
    """Class to validate and test proxies"""
    
    def __init__(self, timeout=5, threads=10, test_urls=None):
        self.timeout = timeout
        self.threads = threads
        self.test_urls = test_urls or [
            "http://httpbin.org/ip",
            "https://httpbin.org/ip",
            "http://example.com",
            "https://example.com"
        ]
        self.results = {}
        self.lock = threading.Lock()
        
    def load_proxy_db(self):
        """Load proxy database if it exists"""
        if os.path.exists(pcont_db_path):
            try:
                with open(pcont_db_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Error reading proxy database. Starting with empty database.")
        return {}
    
    def save_proxy_db(self, db):
        """Save updated proxy database"""
        try:
            os.makedirs(os.path.dirname(pcont_db_path), exist_ok=True)
            with open(pcont_db_path, 'w') as f:
                json.dump(db, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving proxy database: {e}", file=sys.stderr)
            return False
    
    def validate_proxy_format(self, proxy):
        """Validate proxy string format"""
        try:
            if not "://" in proxy:
                return False
                
            protocol, ip, port = extract_protocol_port(proxy)
            
            # Validate protocol
            if protocol not in ["http", "https", "socks4", "socks5"]:
                return False
                
            # Validate IP
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                return False
                
            # Validate port
            try:
                port_num = int(port)
                if port_num < 1 or port_num > 65535:
                    return False
            except ValueError:
                return False
                
            return True
        except:
            return False
    
    def test_proxy_connection(self, proxy):
        """Test if proxy can connect to websites"""
        protocol, ip, port = extract_protocol_port(proxy)
        results = {"working": False, "sites": {}, "avg_response_time": None}
        
        response_times = []
        
        # Skip invalid IPs
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return results
        
        # Test connection to multiple sites
        for url in self.test_urls:
            # Skip HTTPS URLs for SOCKS4 proxies (they don't support HTTPS)
            if protocol == "socks4" and url.startswith("https"):
                continue
                
            results["sites"][url] = {"success": False, "status_code": None, "response_time": None}
            
            try:
                # Set up proxies based on protocol
                proxies = {}
                
                if protocol in ["http", "https"]:
                    proxies = {
                        "http": f"{protocol}://{ip}:{port}",
                        "https": f"{protocol}://{ip}:{port}"
                    }
                elif protocol in ["socks4", "socks5"]:
                    proxies = {
                        "http": f"{protocol}://{ip}:{port}",
                        "https": f"{protocol}://{ip}:{port}"
                    }
                
                # Make request with timeout
                start_time = time.time()
                response = requests.get(url, proxies=proxies, timeout=self.timeout)
                end_time = time.time()
                
                response_time = int((end_time - start_time) * 1000)  # ms
                response_times.append(response_time)
                
                results["sites"][url] = {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": response_time
                }
                
            except requests.exceptions.RequestException:
                pass
        
        # Calculate average response time
        if response_times:
            results["avg_response_time"] = sum(response_times) / len(response_times)
            
        # Determine if proxy is working (at least one successful connection)
        results["working"] = any(site["success"] for site in results["sites"].values())
        
        return results
    
    def test_proxy_anonymity(self, proxy):
        """Test proxy anonymity level"""
        protocol, ip, port = extract_protocol_port(proxy)
        
        # Skip SOCKS proxies for this test
        if protocol in ["socks4", "socks5"]:
            return "unknown"
            
        try:
            # Set up proxies
            proxies = {
                "http": f"{protocol}://{ip}:{port}",
                "https": f"{protocol}://{ip}:{port}"
            }
            
            # Test using a special service that returns headers
            response = requests.get("http://httpbin.org/headers", proxies=proxies, timeout=self.timeout)
            
            if response.status_code == 200:
                headers = response.json().get("headers", {})
                
                # Check for common headers that might reveal the real IP
                if "X-Forwarded-For" in headers or "Client-Ip" in headers:
                    return "transparent"
                elif "Via" in headers or "Proxy-Connection" in headers:
                    return "anonymous"
                else:
                    return "elite"
            
        except:
            pass
            
        return "unknown"
    
    def validate_single_proxy(self, proxy):
        """Validate a single proxy and return results"""
        proxy = proxy.strip()
        
        if not self.validate_proxy_format(proxy):
            return {
                "proxy": proxy,
                "valid_format": False,
                "connection_test": None,
                "anonymity": None,
                "country": None
            }
            
        protocol, ip, port = extract_protocol_port(proxy)
        
        # Get country information
        country_info = get_proxy_details(ip)
        
        # Test connection
        connection_results = self.test_proxy_connection(proxy)
        
        # Test anonymity if connection works
        anonymity = "unknown"
        if connection_results["working"]:
            anonymity = self.test_proxy_anonymity(proxy)
            
        return {
            "proxy": proxy,
            "valid_format": True,
            "connection_test": connection_results,
            "anonymity": anonymity,
            "country": country_info
        }
    
    def validate_proxies(self, proxies, update_db=True):
        """Validate a list of proxies using multiple threads"""
        start_time = time.time()
        total_proxies = len(proxies)
        
        print(f"Starting validation of {total_proxies} proxies using {self.threads} threads")
        print(f"Timeout: {self.timeout} seconds per request")
        
        # Set up progress tracking
        self.completed = 0
        self.working = 0
        
        # Load existing database if updating
        db = self.load_proxy_db() if update_db else {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Submit all tasks
            future_to_proxy = {executor.submit(self.validate_single_proxy, proxy): proxy for proxy in proxies}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    result = future.result()
                    
                    with self.lock:
                        self.completed += 1
                        
                        # Update counters
                        if result["connection_test"] and result["connection_test"]["working"]:
                            self.working += 1
                            
                        # Update results dictionary
                        self.results[proxy] = result
                        
                        # Update database if requested
                        if update_db and result["valid_format"]:
                            protocol, ip, port = extract_protocol_port(proxy)
                            
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
                                    "isp": None,
                                    "anonymity": None
                                }
                            
                            # Update database entry
                            db[proxy]["last_checked"] = datetime.now().isoformat()
                            
                            if result["connection_test"]["working"]:
                                db[proxy]["online_count"] += 1
                                
                                # Update speed
                                if result["connection_test"]["avg_response_time"]:
                                    db[proxy]["speed_history"].append(result["connection_test"]["avg_response_time"])
                                    # Keep only last 5 speed tests
                                    if len(db[proxy]["speed_history"]) > 5:
                                        db[proxy]["speed_history"] = db[proxy]["speed_history"][-5:]
                            else:
                                db[proxy]["offline_count"] += 1
                                
                            # Update country info
                            if result["country"]:
                                db[proxy]["country"] = result["country"].get("country")
                                db[proxy]["countryCode"] = result["country"].get("countryCode")
                                db[proxy]["city"] = result["country"].get("city")
                                db[proxy]["isp"] = result["country"].get("isp")
                                
                            # Update anonymity
                            db[proxy]["anonymity"] = result["anonymity"]
                        
                        # Print progress
                        progress = (self.completed / total_proxies) * 100
                        sys.stdout.write(f"\rProgress: {self.completed}/{total_proxies} " + 
                                        f"({progress:.1f}%) - Working: {self.working}")
                        sys.stdout.flush()
                        
                except Exception as e:
                    print(f"\nError processing proxy {proxy}: {e}", file=sys.stderr)
        
        # Save updated database
        if update_db:
            self.save_proxy_db(db)
            
        # Calculate statistics
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"\n\nValidation completed in {elapsed:.2f} seconds")
        print(f"Total proxies tested: {total_proxies}")
        print(f"Working proxies: {self.working} ({(self.working/total_proxies)*100:.1f}%)")
        print(f"Failed proxies: {total_proxies - self.working} ({((total_proxies-self.working)/total_proxies)*100:.1f}%)")
        
        if update_db:
            print(f"Proxy database updated: {pcont_db_path}")
            
        return self.results
    
    def export_results(self, filename, format="txt", filter_working=True):
        """Export validation results to file"""
        if format == "txt":
            with open(filename, 'w') as f:
                for proxy, result in self.results.items():
                    if filter_working and (not result["connection_test"] or not result["connection_test"]["working"]):
                        continue
                    f.write(f"{proxy}\n")
                    
        elif format == "json":
            with open(filename, 'w') as f:
                # Filter if needed
                if filter_working:
                    filtered_results = {proxy: result for proxy, result in self.results.items()
                                      if result["connection_test"] and result["connection_test"]["working"]}
                    json.dump(filtered_results, f, indent=2)
                else:
                    json.dump(self.results, f, indent=2)
                    
        elif format == "csv":
            with open(filename, 'w') as f:
                # Write header
                f.write("proxy,protocol,ip,port,working,response_time,anonymity,country,country_code\n")
                
                # Write data
                for proxy, result in self.results.items():
                    if filter_working and (not result["connection_test"] or not result["connection_test"]["working"]):
                        continue
                        
                    protocol, ip, port = extract_protocol_port(proxy)
                    working = "Yes" if result["connection_test"] and result["connection_test"]["working"] else "No"
                    response_time = result["connection_test"]["avg_response_time"] if result["connection_test"] else ""
                    anonymity = result["anonymity"] or ""
                    country = result["country"]["country"] if result["country"] else ""
                    country_code = result["country"]["countryCode"] if result["country"] else ""
                    
                    f.write(f"{proxy},{protocol},{ip},{port},{working},{response_time},{anonymity},{country},{country_code}\n")
        
        print(f"Results exported to {filename}")

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Proxy Validator for PConT')
    
    parser.add_argument('--input', '-i', default='free_proxies.txt',
                      help='Input file containing list of proxies')
    parser.add_argument('--output', '-o',
                      help='Output file for validated proxies (default: input file)')
    parser.add_argument('--format', '-f', choices=['txt', 'json', 'csv'], default='txt',
                      help='Output format (default: txt)')
    parser.add_argument('--timeout', '-t', type=int, default=5,
                      help='Timeout for proxy requests in seconds (default: 5)')
    parser.add_argument('--threads', '-n', type=int, default=10,
                      help='Number of parallel threads (default: 10)')
    parser.add_argument('--all', '-a', action='store_true',
                      help='Export all proxies, not just working ones')
    parser.add_argument('--no-db', action='store_true',
                      help='Do not update proxy database')
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_args()
    
    # Set default output to input file if not specified
    if not args.output:
        if args.format == 'txt':
            args.output = args.input
        else:
            base_name = os.path.splitext(args.input)[0]
            args.output = f"{base_name}_validated.{args.format}"
    
    # Load proxies
    try:
        with open(args.input, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        
        print(f"Loaded {len(proxies)} proxies from {args.input}")
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found", file=sys.stderr)
        return 1
    
    # Create validator
    validator = ProxyValidator(timeout=args.timeout, threads=args.threads)
    
    # Validate proxies
    results = validator.validate_proxies(proxies, update_db=not args.no_db)
    
    # Export results
    validator.export_results(args.output, format=args.format, filter_working=not args.all)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
