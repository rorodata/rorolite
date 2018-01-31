"""
    rorolite.project
    ~~~~~~~~~~~~~~~~

    This module implements the project object.
"""
import os
import yaml
from .runtime import Runtime, DEFAULT_RUNTIME

class Project:
    def __init__(self, root="."):
        self.root = root
        self.metadata = self.read_metadata()

    @property
    def runtime(self):
        runtime = self.metadata.get('runtime', DEFAULT_RUNTIME)
        return Runtime.load(runtime)

    def __getitem__(self, key):
        return self.metadata[key]

    def read_metadata(self):
        path = os.path.join(self.root, "rorolite.yml")
        return yaml.safe_load(open(path))
