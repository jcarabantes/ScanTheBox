import os
import subprocess
from modules.output import success, error, info

class Nmap:

    def __init__(self, config_cls):
        
        self.config = config_cls.get_yaml_content()
        self.workspace = config_cls.get_workspace()
        self.output_fullpath = os.path.join(self.workspace, self.config['nmap_common_output'])
        self.hostname = None
        self.last_scan_result = None

    def set_hostname(self, hostname):
        self.hostname = hostname

    def scan_common_tcp_ports(self):
        print(f"Starting nmap scan for common TCP ports on {self.hostname}")
        # print(['nmap', '-Pn', self.hostname, '-oN', self.output_fullpath])
        result = subprocess.run(['nmap', '-Pn', self.hostname, '-oN', self.output_fullpath], capture_output=True, text=True)

        print("Nmap Scan Results for common TCP ports:")
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        # Save the result to a file for further analysis
        self.last_scan_result = result.stdout
    
    def get_common_tcp_ports(self):
        print("Extracting common ports from the scan results")
        return self._extract_tcp_ports(self.last_scan_result)

    def _extract_tcp_ports(self, nmap_output):
        ports = []
        for line in nmap_output.splitlines():
            if '/tcp' in line.lower() and "open" in line.lower():
                port = line.split('/')[0].strip()
                ports.append(port)
        return ports

    def get_open_http(self):
        http_ports = []
        try:
            with open(self.output_fullpath, 'r') as file:
                for line in file:
                    if 'http' in line.lower() and 'open' in line.lower():
                        port = line.split('/')[0].strip()
                        http_ports.append(port)
            return http_ports
        except FileNotFoundError:
            print(f"El archivo {self.output_fullpath} no se encontró.")
            return []
        except Exception as e:
            print(f"Se produjo un error al leer {self.output_fullpath}: {e}")
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