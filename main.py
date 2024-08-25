import argparse
import os
import subprocess
import sys
import time
import requests

# Todo
# 
# workspaces creation
# modules classes
# interactive mode to load workspace and execute specific tasks
# extract http and dns from nmap_fingerprint, that should be independent and should work from the output
# save DNS ouput
# fingerprint nmap
# 445: enum4linux -a solarlab.htb

def create_structure():
    folders = ['files', 'gobuster', 'nmap', 'wordlists']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
    print(f"Created subdirectories: {', '.join(folders)}")

def check_tools():
    required_tools = ['nmap', 'gobuster', 'whatweb', 'dig', 'wfuzz', 'nikto', 'docker']
    missing_tools = []
    
    for tool in required_tools:
        if subprocess.call(f"type {tool}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"Missing tools: {', '.join(missing_tools)}")
        print("Please install the missing tools and try again.")
        exit(1)
    else:
        print("All required tools are installed.")

def check_hostname_responsive(hostname):
    print(f"Checking if hostname {hostname} is responsive")
    response = subprocess.run(['ping', '-c', '1', hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if response.returncode != 0:
        print(f"Hostname {hostname} is not responsive. Please check the hostname and try again.")
        exit(1)
    else:
        print(f"Hostname {hostname} is responsive")

def nmap_all_ports(hostname):
    print(f"Scanning all TCP ports")
    nmap_command = f"xterm -hold -e 'nmap -p- -T4 -Pn {hostname} -oA nmap/all-ports'"
    subprocess.Popen(nmap_command, shell=True)

def nmap_common_tcp_ports(hostname):
    print("Starting nmap scan for common TCP ports")
    output_file_base = os.path.join('nmap', f"common-tcp-ports")
    # result = subprocess.run(['nmap', '-p80', '-Pn', hostname, '-oA', output_file_base], capture_output=True, text=True)
    result = subprocess.run(['nmap', '-Pn', hostname, '-oA', output_file_base], capture_output=True, text=True)
    
    print("Nmap Scan Results for all TCP ports:")
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

    # Extract port numbers from the nmap scan results
    ports = extract_ports(result.stdout)
    return ports

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

def extract_ports(nmap_output):
    ports = []
    lines = nmap_output.splitlines()
    for line in lines:
        if '/tcp' in line:  # Filter lines containing port information
            port = line.split('/')[0].strip()  # Extract the port number
            ports.append(port)
    return ports

def get_whatweb_command(hostname, port):
    return f"xterm -hold -e 'whatweb -a 2 http://{hostname}:{port} | tee whatweb_{hostname}_{port}'"

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
        print("[ERROR] Content-length could not be fetch, vhost bruteforce with wfuzz will not be executed")
        print(e)
        return None

def get_nuclei_command(hostname, port):
#    return f"xterm -hold -e 'docker run --rm -it projectdiscovery/nuclei:latest -target http://{hostname}:{port} | tee nuclei_{hostname}_{port}'"
    return f"docker run --rm -it -v /etc/hosts:/etc/hosts projectdiscovery/nuclei:latest -target http://{hostname}:{port} | tee nuclei_{hostname}_{port}"

def get_nikto_command(hostname, port):
    return f"xterm -hold -e 'nikto -host http://{hostname}:{port} | tee nuclei_{hostname}_{port}'"

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

def get_open_http_ports_from_nmap_output(nmap_output_file):
    http_ports = []
    try:
        with open(nmap_output_file, 'r') as file:
            for line in file:
                if 'http' in line.lower() and 'open' in line.lower():
                    port = line.split('/')[0].strip()
                    http_ports.append(port)
        return http_ports
    except FileNotFoundError:
        print(f"El archivo {nmap_output_file} no se encontró.")
        return []
    except Exception as e:
        print(f"Se produjo un error al leer {nmap_output_file}: {e}")
        return []


def usage():
    print("Usage:")
    print("  scanthebox.py new <hostname>  - Run scans on a new host")
    print("  scanthebox.py load <hostname> - Load and process existing scan data")
    sys.exit(0)

def main():

    parser = argparse.ArgumentParser(description="Process hostname input and perform nmap scans.")
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # Subcomando "new"
    parser_new = subparsers.add_parser('new', help='Start a new scan on the specified hostname')
    parser_new.add_argument('hostname', help='The hostname to process')

    # Subcomando "load"
    parser_load = subparsers.add_parser('load', help='Load an existing scan for the specified hostname')
    parser_load.add_argument('hostname', help='The hostname to load')

    args = parser.parse_args()

    if args.command == 'new':
        hostname = args.hostname
        print(f"Starting new scan for {hostname}")
        # Aquí va la lógica para escanear el nuevo hostname
    elif args.command == 'load':
        hostname = args.hostname
        print("loading...")
        # Aquí va la lógica para cargar un escaneo existente
    else:
        usage()


    # Check for required tools
    check_tools()

    print("Hostname:", hostname)

    # Check if the hostname is responsive
    check_hostname_responsive(hostname)

    # Create a directory with the hostname and set it as the working directory
    if not os.path.exists(hostname):
        os.makedirs(hostname)
    os.chdir(hostname)
    print(f"Created and changed working directory to: {hostname}")

    # Call create_structure() to create additional folders inside the working directory
    create_structure()

    # Perform initial nmap scan to find all TCP ports
    open_ports = nmap_common_tcp_ports(hostname)
    time.sleep(10)
    COMMON_PORTS_OUTPUT = "nmap/common-tcp-ports.nmap"
    http_port_list = get_open_http_ports_from_nmap_output( COMMON_PORTS_OUTPUT )

    if http_port_list:
        spawn_http_tools(hostname, http_port_list)

    # xterm for all ports
    nmap_all_ports( hostname )

    # Perform detailed nmap scans on open ports
    # if open_ports:
    #     nmap_fingerprint(hostname, open_ports)

if __name__ == "__main__":
    main()
