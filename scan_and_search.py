import nmap
import os
import sys
import json
import subprocess

def run_nmap(target):
    nm = nmap.PortScanner()
    nm.scan(target, arguments='-sV')
    return nm.csv()

def save_results(results, filename):
    with open(filename, 'w') as f:
        f.write(results)

def parse_results(filename):
    services = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        header = lines[0].strip().split(';')
        for line in lines[1:]:  # Skip the header line
            parts = line.strip().split(';')
            row = {header[i]: parts[i] for i in range(len(header))}
            services.append({
                'host': row['host'],
                'protocol': row['protocol'],
                'port': int(row['port']),
                'service': row['name'],
                'product': row['product'].split(' ')[0],
                'version': row['version']
            })
    return services

def search_metasploit(services):
    if not services:
        print("No services found. Exiting.")
        return

    for service in services:
        search_query = f"{service['product']} {service['version']}".strip()
        if search_query and service['product']:
            print(f"Searching Metasploit for: {search_query}")
            command = f"msfconsole -q -x 'search {search_query}; exit'"
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            print(output.decode())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <ip_address_or_domain>")
        sys.exit(1)

    target = sys.argv[1]
    results_file = f"{target}_nmap_results.csv"

    print(f"Running Nmap on {target}...")
    nmap_results = run_nmap(target)
    print("Nmap results:\n")
    print(nmap_results)
    save_results(nmap_results, results_file)

    services = parse_results(results_file)
    search_metasploit(services)
