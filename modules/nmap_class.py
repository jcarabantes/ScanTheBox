import os
import subprocess
from modules.output import success, error, info

class Nmap:

    def __init__(self, config_cls):
        
        self.config = config_cls.get_yaml_content()
        self.workspace = config_cls.get_workspace()
        self.output_fullpath = os.path.join(self.workspace, self.config['nmap_all_tcp_output'])
        self.hostname = None
        self.last_scan_result = None

    def set_hostname(self, hostname):
        self.hostname = hostname

    def scan_all_tcp_ports(self):
        info(f"Starting nmap scan for all TCP ports on {self.hostname}")
        # print(['nmap', '-Pn', self.hostname, '-oN', self.output_fullpath])
        result = subprocess.run(['nmap', '-Pn', '-p-', '-T4', self.hostname, '-oN', self.output_fullpath], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        # Save the result to a file for further analysis
        self.last_scan_result = result.stdout
    
    def get_tcp_ports(self):
        print("Extracting all tcp ports from the scan results")
        return self._extract_tcp_ports(self.last_scan_result)

    def _extract_tcp_ports(self, nmap_output):
        ports = []
        for line in nmap_output.splitlines():
            if '/tcp' in line.lower() and "open" in line.lower():
                port = line.split('/')[0].strip()
                ports.append(port)
        return ports

    def get_ports_by_name(self, service_name_list):
        """ service_name_list is a list of nmap string services like
        'dns'
        'http'
        """
        ports = []
        try:
            with open(self.output_fullpath, 'r') as file:
                for line in file:
                    if any(keyword in line.lower() for keyword in service_name_list) and 'open' in line.lower():
                        port = line.split('/')[0].strip()
                        ports.append(port)
            return ports
        except FileNotFoundError:
            print(f"File {self.output_fullpath} not found.")
            return []
        except Exception as e:
            print(f"Error while reading {self.output_fullpath}: {e}")
            return []


    def fingerprint(self, ports):
        info(f"Starting nmap scan for detailed fingerprinting on open ports: {', '.join(ports)}")
        port = ','.join(ports)
        output_file_base = os.path.join('nmap', "/tmp/test.txt")
        result = subprocess.run(['nmap', '-Pn', '-T4', '-sC', '-sV', f'-p{port}', self.hostname, '-oA', output_file_base], capture_output=True, text=True)
        info(f"Nmap Scan Results for port {port}:")
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        # Identify HTTP and DNS services and create respective lists of ports
        # http_ports = []
        # dns_ports = []
        # for line in result.stdout.splitlines():
        #     if 'http' in line.lower() and "open" in line.lower():
        #         port = line.split('/')[0].strip()
        #         http_ports.append(port)
        #     if 'domain' in line.lower() and "open" in line.lower():
        #         port = line.split('/')[0].strip()
        #         dns_ports.append(port)

        # If there are HTTP ports, spawn xterm windows for whatweb and gobuster
        # if http_ports:
        #     spawn_http_tools(hostname, http_ports)
        
        # If there are DNS ports, call DNS fingerprinting functions
        # if dns_ports:
        #     dns_query(hostname)