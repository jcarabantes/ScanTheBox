import cmd
import os
from modules.nmap_class import Nmap

# Shell interactiva utilizando el módulo Cmd
class ScanShell(cmd.Cmd):
    intro = "Interactive shell for scanning commands. Type help or ? to list commands.\n"
    prompt = "(ScanTheBox) "

    def __init__(self, hostname, config):
        super().__init__()
        self.hostname = hostname
        self.config = config

    # Comando para ver el estado
    def do_status(self, arg):
        """Check the status of the scan"""
        print(f"Checking scan status for {self.hostname}...")

    # Comando para ejecutar nmap
    def do_nmap(self, arg):
        """Run an nmap scan on the hostname"""
        # print(f"Running nmap scan on {self.hostname}...")
        # os.system(f"nmap -sC -sV {self.hostname}")
        n = Nmap(self.config)
        print(self.config)
        n.scan_common_tcp_ports(self.hostname)
        open_ports = n.get_common_tcp_ports()

        http_port_list = n.get_open_http()
        print("http ports")
        print(http_port_list)

    # Comando para salir de la shell
    def do_exit(self, arg):
        """Exit the interactive shell"""
        print("Exiting shell.")
        return True

    def do_help(self, arg):
        """List available commands"""
        cmd.Cmd.do_help(self, arg)

    # Si ingresan un comando desconocido
    def default(self, line):
        print(f"Unknown command: {line}")
