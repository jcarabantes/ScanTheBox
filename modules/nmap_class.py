import os
import subprocess

class Nmap:
    def __init__(self, config):
        self.output_dir = config.get('nmap_output_dir', 'nmap/common-tcp-ports')
        self.hostname = None

    def scan_common_tcp_ports(self, hostname):
        self.hostname = hostname
        print(f"Starting nmap scan for common TCP ports on {hostname}")
        output_file_base = os.path.join(self.output_dir)
        result = subprocess.run(['nmap', '-Pn', hostname, '-oA', output_file_base], capture_output=True, text=True)

        print("Nmap Scan Results for common TCP ports:")
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        # Save the result to a file for further analysis
        self.last_scan_result = result.stdout
    
    def get_common_tcp_ports(self):
        print("Extracting common ports from the scan results")
        return self.extract_ports(self.last_scan_result)

    def extract_ports(self, nmap_output):
        ports = []
        for line in nmap_output.splitlines():
            if '/tcp' in line.lower() and "open" in line.lower():
                port = line.split('/')[0].strip()
                ports.append(port)
        return ports
