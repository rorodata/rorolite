"""Deployment flow.
"""
import os
import yaml
import tempfile
import shutil
from fabric.api import env
import fabric.api as remote
from . import fabfile

SUPERVISOR_CONFIG = """
[progam:{name}]
command = {command}
directory = {directory}
redirect_stderr = true
stdout_logfile = /var/log/supervisor/%(program_name)s.log
"""

class Deployment:
    def __init__(self, directory="."):
        self.directory = directory
        self.config = None

    def read_config(self, root):
        path = os.path.join(root, "roro.yml")
        return yaml.safe_load(open(path).read())

    def deploy(self):
        self.config = self.read_config(self.directory)
        if "host" not in self.config:
            raise Exception("Missing required field in roro.yml: host")

        self.push_directory()

    def push_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            archive = self.archive(tmpdir)
            remote.put(archive, "/tmp/rorolite-project.tgz")
            remote.sudo("mkdir -p /opt/rorolite/project")
            with remote.cd("/opt/rorolite/project"):
                remote.sudo("chown {} .".format(env.user))
                remote.run("tar xzf /tmp/rorolite-project.tgz")
                self.setup_virtualenv()

    def setup_virtualenv(self):
        remote.run("virtualenv -p /opt/ananconda3/python3 .rorolite/env")
        if os.path.exists("requirements.txt"):
            remote.run(".rorolite/env/bin/pip install -r requirements.txt")

    def archive(self, rootdir, format='gztar'):
        base_name = os.path.join(rootdir, "rorolite-project")
        return shutil.make_archive(base_name, format, base_dir=".")

