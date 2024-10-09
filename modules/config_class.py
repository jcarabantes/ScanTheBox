import sys
import os
import yaml

class Config:

    def __init__(self, config_file, hostname):
        self.hostname = hostname
        self.ip = self._get_ip_from_etc_hosts()
        # Define the configuration file path and root directory
        self.root_directory = os.path.dirname(__file__) + "/../"
        self.config_path = os.path.join(self.root_directory, config_file)
        self.workspace = self.root_directory + hostname + "/"
        # Parse the YAML configuration file
        self.config = self.parse_yaml(self.config_path)
        self._check_wordlists()


    def _get_ip_from_etc_hosts(self):
        try:
            with open('/etc/hosts', 'r') as hosts_file:
                for line in hosts_file:
                    l = line.strip()
                    if f"{self.hostname}" in l:
                        return l.split()[0]
            print(f"Hostname {self.hostname} not found in /etc/hosts")
            return None
        except FileNotFoundError:
            print("/etc/hosts file not found")
            return None
        except Exception as e:
            print(f"An error occurred while reading /etc/hosts: {e}")
            return None

    def _check_wordlists(self):
        """
        Private method to check if the wordlist files exist.
        If a wordlist file is missing, raise an error and stop execution.
        """
        wordlists = self.config.get('wordlists', {})
        
        for key, path in wordlists.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"Wordlist '{key}' not found at {path}")


    def get_yaml_content(self):
        return self.config

    def get_config_path(self):
        return self.config_path

    def get_workspace(self):
        return self.workspace

    def parse_yaml(self, config_path):
        # Load and parse the YAML file
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: The config file {config_path} was not found.")
            return {}
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML file {config_path}: {exc}")
            return {}