import subprocess
import os
import yaml
import sys
from modules.output import success, error, info


def check_required_modules():
    required_modules = ['argparse', 'os', 'yaml', 'termcolor', 'cmd']
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        error(f"Error: The following modules are not installed: {', '.join(missing_modules)}")
        error("Install them by running: pip install <module>")
        sys.exit(1)


def usage():
    print("Usage:")
    print("  scanthebox.py new <hostname>  - Run scans on a new host")
    print("  scanthebox.py load <hostname> - Load and process existing scan data")
    sys.exit(0)

def parse_yaml(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def check_tools():
    required_tools = ['xterm', 'nmap', 'gobuster', 'whatweb', 'dig', 'wfuzz', 'nikto', 'docker', 'nxc', 'smbmap', 'enum4linux-ng']
    missing_tools = []
    
    for tool in required_tools:
        if subprocess.call(f"type {tool}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        error(f"Missing tools: {', '.join(missing_tools)}")
        error("Please install the missing tools and try again.")
        exit(1)
    else:
        success("All required tools are installed.")

def check_hostname_responsive(hostname):
    info(f"Checking if hostname {hostname} is responsive")
    response = subprocess.run(['ping', '-c', '1', hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if response.returncode != 0:
        error(f"Hostname {hostname} is not responsive. Please check the hostname and try again.")
        exit(1)
    else:
        success(f"Hostname {hostname} is responsive")

def create_structure():
    folders = ['files', 'gobuster', 'nmap', 'wordlists', 'smb']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
    success(f"Created subdirectories: {', '.join(folders)}")

