from __future__ import print_function
import os
import sys
import yaml

class Config:
    def __init__(self, config):
        self.config = config

        if "host" not in self.config:
            raise Exception("Missing required field in the config file: host")

        self.host = config['host']
        self.user = config.get('user') or os.getlogin()

    @staticmethod
    def load(filename):
        config = yaml.safe_load(open(filename))
        return Config(config)

def load_config(directory):
    path = os.path.join(directory, "rorolite.yml")
    if not os.path.exists(path):
        print("Unable to find rorolite.yml file", file=sys.stderr)
        sys.exit(1)
    return Config.load(path)
