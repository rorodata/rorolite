"""
    rorolite.project
    ~~~~~~~~~~~~~~~~

    This module implements the project object.
"""
import os
import yaml
from .runtime import Runtime

class Project:
    def __init__(self, root="."):
        self.root = root
        self.metadata = self.read_metadata()

    @property
    def runtime(self):
        return Runtime.load(self['runtime'])

    def __getitem__(self, key):
        return self.metadata[key]

    def read_metadata(self):
        path = os.path.join(self.root, "rorolite.yml")
        return yaml.safe_load(open(path))
