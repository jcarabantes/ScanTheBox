import os
import subprocess

class Nmap:
    def __init__(self, config):
        self.output_fullpath = os.path.join(config['nmap_output_file'])
        self.hostname = None
        self.last_scan_result = None

    def scan_common_tcp_ports(self, hostname):
        self.hostname = hostname
        print(f"Starting nmap scan for common TCP ports on {hostname}")
        result = subprocess.run(['nmap', '-Pn', hostname, '-oN', self.output_fullpath], capture_output=True, text=True)

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