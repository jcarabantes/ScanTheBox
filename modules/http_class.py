import subprocess
from modules.output import success, error, info

class Http:

    def __init__(self, http_port_list, config_cls):
        # Define the configuration file path and root directory
        # self.root_directory = os.path.dirname(__file__) + "/../"
        # self.config_path = os.path.join(self.root_directory, config_file)
        # self.workspace = self.root_directory + hostname + "/"
        # Parse the YAML configuration file
        self.config = config_cls.get_yaml_content()
        self.http_port_list = http_port_list

    def set_hostname(self, hostname):
        self.hostname = hostname

    def get_gobuster_command(self, port, wordlist):
        basename = wordlist.split("/")[-1:][0]
        info(f"xterm -hold -e 'gobuster dir -u http://{self.hostname}:{port} -w {wordlist} -o gobuster/gobuster_{basename}_{self.hostname}_{port}'")
        return f"xterm -hold -e 'gobuster dir -u http://{self.hostname}:{port} -w {wordlist} -o gobuster/gobuster_{basename}_{self.hostname}_{port}'"


    def spawn_tools(self):
        for port in self.http_port_list:
            info(f"HTTP service detected on port {port}, spawning xterm windows for whatweb and gobuster")
            # whatweb_command = get_whatweb_command(hostname, port)
            
            gobuster_common = self.get_gobuster_command(port, self.config['wordlists']['common'])
            gobuster_files = self.get_gobuster_command(port, self.config['wordlists']['files'])
            gobuster_directories = self.get_gobuster_command(port, self.config['wordlists']['directories'])
            
            # vhost_bruteforce_command = get_vhost_wfuzz_command(hostname, port, "/home/remnux/SecLists/Discovery/DNS/namelist.txt")
            # nuclei_command = get_nuclei_command(hostname, port)
            # nikto_command = get_nikto_command(hostname, port)


            # subprocess.Popen(whatweb_command, shell=True)
            subprocess.Popen(gobuster_common, shell=True)
            subprocess.Popen(gobuster_files, shell=True)
            subprocess.Popen(gobuster_directories, shell=True)
            # if vhost_bruteforce_command:
            #     subprocess.Popen(vhost_bruteforce_command, shell=True)
            
            # # when using docker, we need to use os.system(): https://stackoverflow.com/questions/59507395/how-do-i-use-python-to-launch-an-interactive-docker-container
            # os.system(nuclei_command)

            # subprocess.Popen(nikto_command, shell=True)

