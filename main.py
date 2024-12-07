import os
import time
import random
import threading
import requests
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

# === Utility Functions ===

def print_banner():
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════╗
║          BlockMesh Network AutoBot           ║
║     Github: https://github.com/IM-Hanzou     ║
║      Welcome and do with your own risk!      ║
╚══════════════════════════════════════════════╝
"""
    print(banner)

def generate_metric(min_val, max_val, decimals=2):
    """Generate random float within a range."""
    return round(random.uniform(min_val, max_val), decimals)

def get_ip_info(ip_address):
    """Fetch IP information using an external API."""
    try:
        response = requests.get(f"https://ipwhois.app/json/{ip_address}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as err:
        print(f"{Fore.RED}Failed to get IP info: {err}")
        return None

def format_proxy(proxy_string):
    """Format proxy details into a dictionary."""
    proxy_type, address = proxy_string.split("://")
    if "@" in address:
        creds, host_port = address.split("@")
        username, password = creds.split(":")
        host, port = host_port.split(":")
        return {
            "http": f"{proxy_type}://{username}:{password}@{host}:{port}",
            "https": f"{proxy_type}://{username}:{password}@{host}:{port}"
        }, host
    else:
        host, port = address.split(":")
        return {
            "http": f"{proxy_type}://{host}:{port}",
            "https": f"{proxy_type}://{host}:{port}"
        }, host

# === Core Functionalities ===

def authenticate(email, password, proxy, headers):
    """Authenticate and get API token."""
    proxy_config, ip_address = format_proxy(proxy)
    login_data = {"email": email, "password": password}
    try:
        response = requests.post(
            "https://api.blockmesh.xyz/api/get_token",
            json=login_data,
            headers=headers,
            proxies=proxy_config
        )
        response.raise_for_status()
        return response.json().get("api_token"), ip_address
    except requests.RequestException as err:
        print(f"{Fore.RED}Login failed: {ip_address}: {err}")
        return None, ip_address

def submit_data(url, payload, headers, proxies):
    """Submit bandwidth or task data."""
    try:
        response = requests.post(url, json=payload, headers=headers, proxies=proxies)
        response.raise_for_status()
        print(f"{Fore.GREEN}Data submitted successfully.")
    except requests.RequestException as err:
        print(f"{Fore.RED}Failed to submit data: {err}")

def process_proxy(email, password, proxy, headers):
    """Process each proxy."""
    first_run = True
    while True:
        if first_run:
            api_token, ip_address = authenticate(email, password, proxy, headers)
            first_run = False
        else:
            _, ip_address = format_proxy(proxy)
        
        if api_token:
            proxy_config, _ = format_proxy(proxy)
            ip_info = get_ip_info(ip_address)

            if ip_info:
                # Submit bandwidth
                submit_data(
                    "https://app.blockmesh.xyz/api/submit_bandwidth",
                    {
                        "email": email,
                        "api_token": api_token,
                        "download_speed": generate_metric(0.0, 10.0),
                        "upload_speed": generate_metric(0.0, 5.0),
                        "latency": generate_metric(20.0, 300.0),
                        "city": ip_info.get("city", "Unknown"),
                        "country": ip_info.get("country_code", "XX"),
                        "ip": ip_info.get("ip", ""),
                        "asn": ip_info.get("asn", "AS0").replace("AS", ""),
                        "colo": "Unknown"
                    },
                    headers,
                    proxy_config
                )

                # Simulate task handling
                time.sleep(random.randint(60, 120))

        time.sleep(10)

# === Main Logic ===

def main():
    print_banner()
    email = input(f"{Fore.LIGHTBLUE_EX}Enter Email: {Style.RESET_ALL}")
    password = input(f"{Fore.LIGHTBLUE_EX}Enter Password: {Style.RESET_ALL}")

    # Headers
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "https://app.blockmesh.xyz",
        "user-agent": "Mozilla/5.0"
    }

    # Load proxies
    proxy_file = "proxies.txt"
    if not os.path.exists(proxy_file):
        print(f"{Fore.RED}[×] proxies.txt not found!")
        return

    with open(proxy_file, "r") as file:
        proxies = file.read().splitlines()

    print(f"{Fore.GREEN}[✓] Loaded {len(proxies)} proxies from proxies.txt")

    # Start threads
    threads = []
    for proxy in proxies:
        thread = threading.Thread(target=process_proxy, args=(email, password, proxy, headers))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(1)

    print(f"{Fore.LIGHTCYAN_EX}All threads started. Monitoring...")


if __name__ == "__main__":
    main()
