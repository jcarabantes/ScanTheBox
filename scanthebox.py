import argparse
import os
import subprocess
import sys
import time
import requests
import yaml
from modules.nmap_class import Nmap
from modules.config_class import Config
from modules.utils import check_tools, check_hostname_responsive, create_structure, usage, parse_yaml, check_required_modules
from modules.output import success, error, info
from modules.loader_prompt import ScanShell


# Todo
# remove pycache from the repository + gitignore it
# Create the HTTP module
# extract http and dns from nmap_fingerprint, that should be independent and should work from the output
# save DNS ouput
# fingerprint nmap
# 445: enum4linux -a solarlab.htb
# improve de load module
    # on load, check if workspace already existss

def nmap_all_ports(hostname):
    print(f"Scanning all TCP ports")
    nmap_command = f"xterm -hold -e 'nmap -p- -T4 -Pn {hostname} -oA nmap/all-ports'"
    subprocess.Popen(nmap_command, shell=True)

def nmap_fingerprint(hostname, ports):
    print(f"Starting nmap scan for detailed fingerprinting on open ports: {', '.join(ports)}")
    port = ','.join(ports)
    output_file_base = os.path.join('nmap', f"{hostname}-ports-fingerprint")
    result = subprocess.run(['nmap', '-T4', '-sC', '-sV', f'-p{port}', hostname, '-oA', output_file_base], capture_output=True, text=True)
    print(f"Nmap Scan Results for port {port}:")
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

    # Identify HTTP and DNS services and create respective lists of ports
    http_ports = []
    dns_ports = []
    for line in result.stdout.splitlines():
        if 'http' in line.lower() and "open" in line.lower():
            port = line.split('/')[0].strip()
            http_ports.append(port)
        if 'domain' in line.lower() and "open" in line.lower():
            port = line.split('/')[0].strip()
            dns_ports.append(port)

    # If there are HTTP ports, spawn xterm windows for whatweb and gobuster
    if http_ports:
        spawn_http_tools(hostname, http_ports)
    
    # If there are DNS ports, call DNS fingerprinting functions
    if dns_ports:
        dns_query(hostname)

def get_whatweb_command(hostname, port):
    return f"xterm -hold -e 'whatweb -a 4 http://{hostname}:{port} 2> /dev/null| tee whatweb_{hostname}_{port}'"

def get_gobuster_command(hostname, port, wordlist):
    basename = wordlist.split("/")[-1:][0]
    return f"xterm -hold -e 'gobuster -u http://{hostname}:{port} -w {wordlist} -o gobuster/gobuster_{basename}_{hostname}_{port}'"

def get_vhost_wfuzz_command(hostname, port, wordlist):
    # We first need to know what's the content-length when 
    # we request a non-existent virtual host
    response = requests.get(headers={"Host": f"nonexistent.{hostname}"},url=f"http://{hostname}:{port}", allow_redirects=False)

    try:
        cl = response.headers['Content-Length']
        print(f"Content-length when invalid vhost is checked is: {cl}")
        return f'wfuzz -c -w {wordlist} -H "Host: FUZZ.{hostname}" --hh {cl} http://{hostname}'
    except Exception as e:
        print("[ERROR] Unable to retrieve the Content-length Header. Automatic wfuzz could not be executed")
        print("[ERROR] Consider execute wfuzz manually")
        print(e)
        return None

def get_nuclei_command(hostname, port):
#    return f"xterm -hold -e 'docker run --rm -it projectdiscovery/nuclei:latest -target http://{hostname}:{port} | tee nuclei_{hostname}_{port}'"
    return f"docker run --rm -it -v /etc/hosts:/etc/hosts projectdiscovery/nuclei:latest -target http://{hostname}:{port} | tee nuclei_{hostname}_{port}"

def get_nikto_command(hostname, port):
    return f"xterm -hold -e 'nikto -host http://{hostname}:{port} | tee nikto_{hostname}_{port}'"

def spawn_http_tools(hostname, ports):
    for port in ports:
        print(f"HTTP service detected on port {port}, spawning xterm windows for whatweb and gobuster")
        whatweb_command = get_whatweb_command(hostname, port)
        
        gobuster_command_common = get_gobuster_command(hostname, port, "/usr/share/dirb/wordlists/common.txt")
        gobuster_command_files = get_gobuster_command(hostname, port, "/home/remnux/SecLists/Discovery/Web-Content/raft-medium-files.txt")
        gobuster_command_directories = get_gobuster_command(hostname, port, "/home/remnux/SecLists/Discovery/Web-Content/raft-medium-directories.txt")
        
        vhost_bruteforce_command = get_vhost_wfuzz_command(hostname, port, "/home/remnux/SecLists/Discovery/DNS/namelist.txt")
        nuclei_command = get_nuclei_command(hostname, port)
        nikto_command = get_nikto_command(hostname, port)


        subprocess.Popen(whatweb_command, shell=True)
        subprocess.Popen(gobuster_command_common, shell=True)
        subprocess.Popen(gobuster_command_files, shell=True)
        subprocess.Popen(gobuster_command_directories, shell=True)
        if vhost_bruteforce_command:
            subprocess.Popen(vhost_bruteforce_command, shell=True)
        
        # when using docker, we need to use os.system(): https://stackoverflow.com/questions/59507395/how-do-i-use-python-to-launch-an-interactive-docker-container
        os.system(nuclei_command)

        subprocess.Popen(nikto_command, shell=True)

def dns_query(hostname):
    dns_server = get_ip_from_etc_hosts( hostname )
    domain = hostname

    record_types = ["A", "MX", "NS", "TXT", "CNAME", "SRV", "ANY"]
    for record_type in record_types:
        subprocess.run(['dig', f'@{dns_server}', domain, record_type], check=True)
    # Attempt zone transfer (AXFR)
    subprocess.run(['dig', f'@{dns_server}', domain, 'AXFR'], check=True)

def get_ip_from_etc_hosts(hostname):
    try:
        with open('/etc/hosts', 'r') as hosts_file:
            for line in hosts_file:
                l = line.strip()
                if f"{hostname}" in l:
                    return l.split()[0]
        print(f"Hostname {hostname} not found in /etc/hosts")
        return None
    except FileNotFoundError:
        print("/etc/hosts file not found")
        return None
    except Exception as e:
        print(f"An error occurred while reading /etc/hosts: {e}")
        return None

def main():

    parser = argparse.ArgumentParser(description="Process hostname input and perform nmap scans.")
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # Options to create a new scan
    parser_new = subparsers.add_parser('new', help='Start a new scan on the specified hostname')
    parser_new.add_argument('hostname', help='The hostname to process')

    # Options to load an existing hostname
    parser_load = subparsers.add_parser('load', help='Load an existing scan for the specified hostname')
    parser_load.add_argument('hostname', help='The hostname to load')

    args = parser.parse_args()

    # Check for required tools
    # check_tools()
    hostname = args.hostname
    info(f"Hostname: {hostname}")

    config_file = "scanthebox.yaml"
    cfg = Config(config_file, hostname)

    if args.command == 'new':
        info(f"Starting new scan for {hostname}")
        # Check if the hostname is responsive
        check_hostname_responsive(hostname)

        # Create a directory with the hostname and set it as the working directory
        if not os.path.exists(hostname):
            os.makedirs(hostname)
        os.chdir(hostname)
        info(f"Created and changed working directory to: {hostname}")

        # Call create_structure() to create additional folders inside the working directory
        create_structure()

        nmap = Nmap(cfg)
        nmap.scan_common_tcp_ports(hostname)
        open_ports = nmap.get_common_tcp_ports()

        time.sleep(2)

        http_port_list = nmap.get_open_http()
        print("http ports")
        print(http_port_list)
        sys.exit(1)


    elif args.command == 'load':
        info(f"Loading scan for {hostname}. Entering interactive shell...")
        
        shell = ScanShell(hostname, cfg)
        shell.cmdloop()
        sys.exit(0)
    else:
        usage()
  


    # new HTTP(http_port_list)

    if http_port_list:
        spawn_http_tools(hostname, http_port_list)

    # xterm for all ports
    nmap_all_ports( hostname )

    # Perform detailed nmap scans on open ports
    # if open_ports:
    #     nmap_fingerprint(hostname, open_ports)

if __name__ == "__main__":
    check_required_modules()
    main()
