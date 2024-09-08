import cmd
import os
from modules.nmap_class import Nmap

class ScanShell(cmd.Cmd):
    intro = "Interactive shell for scanning commands. Type help or ? to list commands.\n"
    prompt = None

    def __init__(self, hostname, config):
        super().__init__()
        self.hostname = hostname
        self.config = config
        self.prompt = f"(stb/{hostname}) > "

    def do_status(self, arg):
        """Check the status of the scan"""
        print(f"Checking scan status for {self.hostname}...")

    def do_nmap(self, arg):
        """Run an nmap scan on the hostname"""
        nmap = Nmap(self.config)
        nmap.scan_common_tcp_ports(self.hostname)
        open_ports = nmap.get_common_tcp_ports()

        http_port_list = nmap.get_open_http()
        print("http ports")
        print(http_port_list)


    def do_exit(self, arg):
        """Exit the interactive shell"""
        print("Exiting shell.")
        return True

    def do_help(self, arg):
        """List available commands"""
        cmd.Cmd.do_help(self, arg)

    def default(self, line):
        print(f"Unknown command: {line}")
