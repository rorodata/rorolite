
class Config:
    def __init__(self, config):
        self.config = config

        if "host" not in self.config:
            raise Exception("Host parameter is required")

    @staticmethod
    def load(filename):
        config = yaml.safe_load(filename)
        return Config(config)

def load_config(directory):
    path = os.path.join(directory, "roro.yml")
    return Config.load(path)

system_packages = [
    "supervisor",
    "python-virtualenv"
]
anaconda_version = "5.0.0"

anaconda_download_url_format = "https://repo.continuum.io/archive/Anaconda3-{version}-Linux-x86_64.sh"

root_directory = "/tmp"

services = []


