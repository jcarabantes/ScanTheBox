import argparse
import os
import sys
import subprocess
import time
import requests
# import yaml
from modules.nmap_class import Nmap
from modules.http_class import Http
from modules.dns_class import Dns
from modules.smb_class import Smb
from modules.config_class import Config
from modules.utils import check_tools, check_hostname_responsive, create_structure, usage, parse_yaml, check_required_modules, check_http
from modules.output import success, error, info
from modules.loader_prompt import ScanShell

def get_whatweb_command(hostname, port):
    return f"xterm -hold -e 'whatweb -a 4 http://{hostname}:{port} 2> /dev/null| tee whatweb_{hostname}_{port}'"

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
    check_tools()
    hostname = args.hostname
    info(f"Hostname: {hostname}")

    config_file = "scanthebox.yaml"
    cfg = Config(config_file, hostname)

    if args.command == 'new':

        # Create a directory with the hostname and set it as the working directory
        if os.path.exists(hostname):
            error(f"Error, {hostname} has been already scanned.")
            sys.exit(0)
        else:
            os.makedirs(hostname)
        os.chdir(hostname)

        info(f"Starting new scan for {hostname}")
        info(f"Created and changed working directory to: {hostname}")

        # Check if the hostname is responsive
        check_hostname_responsive(hostname)
        # Call create_structure() to create additional folders inside the working directory
        create_structure()

        nmap = Nmap(cfg)
        nmap.set_hostname(hostname)
        nmap.scan_all_tcp_ports()
        open_ports = nmap.get_tcp_ports()

        # lets execute -sC and -sV on each common port
        nmap.fingerprint(open_ports)

        http_port_list = check_http(hostname, open_ports)
        dns_port_list = nmap.get_ports_by_name(['dns', 'domain'])
        smb_port_list = nmap.get_ports_by_name(['smb', 'microsoft-ds'])
        
        if http_port_list:
            http = Http(http_port_list, cfg)
            http.set_hostname(hostname)
            http.spawn_tools()

        if dns_port_list:
            dns = Dns(cfg)
            dns.dns_query()

        if smb_port_list:
            smb = Smb(smb_port_list, cfg)
            smb.set_hostname(hostname)
            smb.spawn_tools()


        sys.exit(1)


    elif args.command == 'load':
        info(f"Changed working directory to: {hostname}")
        info(f"Loading scan for {hostname}. Entering interactive shell...")
        os.chdir(hostname)
        shell = ScanShell(hostname, cfg)
        shell.cmdloop()
        sys.exit(0)
    else:
        usage()

if __name__ == "__main__":
    check_required_modules()
    main()
