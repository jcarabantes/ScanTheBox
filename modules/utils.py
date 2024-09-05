import subprocess
import os
import yaml
from modules.output import success, error, info

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
    required_tools = ['nmap', 'gobuster', 'whatweb', 'dig', 'wfuzz', 'nikto', 'docker']
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
        print(f"Hostname {hostname} is not responsive. Please check the hostname and try again.")
        exit(1)
    else:
        print(f"Hostname {hostname} is responsive")

def create_structure():
    folders = ['files', 'gobuster', 'nmap', 'wordlists']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
    print(f"Created subdirectories: {', '.join(folders)}")

