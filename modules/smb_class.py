import subprocess
from modules.output import success, error, info

class Smb:

    def __init__(self, smb_port_list, config_cls):
        # Define the configuration file path and root directory
        # self.root_directory = os.path.dirname(__file__) + "/../"
        # self.config_path = os.path.join(self.root_directory, config_file)
        # self.workspace = self.root_directory + hostname + "/"
        # Parse the YAML configuration file
        self.config = config_cls.get_yaml_content()
        self.smb_port_list = smb_port_list

    def set_hostname(self, hostname):
        self.hostname = hostname

    def get_smbmap_command(self):
        info(f"smbmap -H {self.hostname}  -u 'guest' -p '' 2> /dev/null | tee smb/smbmap_{self.hostname}")
        return f"smbmap -H {self.hostname}  -u 'guest' -p '' 2> /dev/null | tee smb/smbmap_{self.hostname}"

    def get_ridbrute_command(self):
        info(f"nxc smb {self.hostname} -u 'guest -p '' --rid-brute 2> /dev/null | tee smb/nxc_ridbrute_{self.hostname}")
        return f"nxc smb {self.hostname} -u 'guest' -p '' --rid-brute 2> /dev/null | tee smb/nxc_ridbrute_{self.hostname}"

    def get_enum4linx_ng_command(self):
        info(f"enum4linux-ng {self.hostname} -u 'guest' -p '' -A -C 2> /dev/null | tee smb/enum4linux_ng_{self.hostname}")
        return f"enum4linux-ng {self.hostname} -u 'guest' -p '' -A -C 2> /dev/null | tee smb/enum4linux_ng_{self.hostname}"



    def spawn_tools(self):
        for port in self.smb_port_list:
            info(f"SMB service detected on port {port}, spawning xterm windows for smbmap, nxc and enum4linux-ng")
            
            smbmap_nullsession = self.get_smbmap_command()
            nxc_ridbrute = self.get_ridbrute_command()
            enum4linux_ng = self.get_enum4linx_ng_command()

            subprocess.Popen(smbmap_nullsession, shell=True)
            subprocess.Popen(nxc_ridbrute, shell=True)
            info("warning: enum4linux-ng will produce output at the end of the process. check ps auxw to see if is still in execution")
            subprocess.Popen(enum4linux_ng, shell=True)

