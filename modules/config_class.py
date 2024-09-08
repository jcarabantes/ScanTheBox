import sys
import os
import yaml

class Config:
    def __init__(self, config_file, hostname):
        # Define the configuration file path and root directory
        self.root_directory = os.path.dirname(__file__) + "/../"
        self.config_path = os.path.join(self.root_directory, config_file)
        self.workspace = self.root_directory + hostname + "/"
        # Parse the YAML configuration file
        self.config = self.parse_yaml(self.config_path)

    def get_yaml_content(self):
        return self.config

    def get_config_path(self):
        return self.config_path

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