"""Deployment flow.
"""
import os
import pathlib
import yaml
import tempfile
import shutil
from fabric.api import env, sudo, lcd
import fabric.api as remote
from .project import Project

SUPERVISOR_CONFIG = """
[program:{name}]
command = {command}
directory = {directory}
redirect_stderr = true
stdout_logfile = /var/log/supervisor/%(program_name)s.log
environment =
    PATH="/opt/rorolite/project/.rorolite/env/bin:%(ENV_PATH)s"
"""

class Deployment:
    def __init__(self, directory="."):
        self.project = Project(directory)
        self.directory = directory
        self.config = None
        self.version = 0
        self.deploy_root = None

    def read_config(self, root):
        path = os.path.join(root, "rorolite.yml")
        return yaml.safe_load(open(path).read())

    def deploy(self):
        self.config = self.read_config(self.directory)
        if "host" not in self.config:
            raise Exception("Missing required field in rorolite.yml: host")

        self.version = self.find_current_version() + 1
        self.deploy_root = "/opt/rorolite/deploys/{}".format(self.version)
        print("Deploying project version {}...".format(self.version))

        remote.sudo("mkdir -p " + self.deploy_root)

        self.push_directory()
        self.setup_virtualenv()

        remote.sudo("ln -sfT {} /opt/rorolite/project".format(self.deploy_root))

        self.restart_services()

    def find_current_version(self):
        output = remote.run("ls /opt/rorolite/deploys 2>/dev/null || echo", quiet=True)
        versions = [int(v) for v in output.strip().split() if v.isnumeric()]
        return versions and max(versions) or 0

    def push_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            archive = self.archive(rootdir=".", output_dir=tmpdir)
            remote.put(archive, "/tmp/rorolite-project.tgz")

            with lcd(tmpdir):
                self.generate_supervisor_config(rootdir=tmpdir)

                supervisor_archive = self.archive(tmpdir, base_dir=".rorolite", filename="rorolite-supervisor")
                remote.put(supervisor_archive, "/tmp/rorolite-supervisor.tgz")

            with remote.cd(self.deploy_root):
                remote.sudo("chown {} .".format(env.user))
                remote.run("tar xzf /tmp/rorolite-project.tgz")
                remote.run("tar xzf /tmp/rorolite-supervisor.tgz")

    def setup_virtualenv(self):
        print("setting up virtualenv...")
        with remote.cd(self.deploy_root):
            python_binary = self.project.runtime.python_binary
            remote.run("{python} -m virtualenv --system-site-packages -p {python} .rorolite/env".format(python=python_binary))
            if os.path.exists("requirements.txt"):
                # install all the application dependencies
                remote.run(".rorolite/env/bin/pip install -r requirements.txt")

    def archive(self, rootdir, output_dir=None, format='gztar', base_dir=".", filename='rorolite-project'):
        output_dir = output_dir or rootdir
        base_name = os.path.join(output_dir, filename)
        return shutil.make_archive(base_name, format, root_dir=rootdir, base_dir=base_dir)

    def restart_services(self):
        services = self.config.get('services', [])
        # TODO: validate services
        sudo("rm -rf /etc/supervisor/conf.d && ln -sfT /opt/rorolite/project/.rorolite/supervisor /etc/supervisor/conf.d")
        sudo("supervisorctl update")

        if not services:
            print("Deploy successful. No services found.")
            return

        for s in services:
            sudo("supervisorctl restart {}".format(s['name']))

        host = self.config['host']
        print("Services are live at:")
        for s in services:
            print("  {} -- http://{}:{}/".format(s['name'], host, s['port']))

    def generate_supervisor_config(self, rootdir):
        # Create the supervisor directory
        path = pathlib.Path(rootdir).joinpath(".rorolite", "supervisor")

        # XXX-Anand: Jan 2018
        # Passing exist_ok to mkdir is failing mysteriously.
        # This very function is working fine when called indepenently.
        # May be there is some monkey-patching going on in Fabric.
        # The following work-around takes care of it.
        if not path.exists():
            path.mkdir(parents=True)

        services = self.config.get('services', [])
        for s in services:
            self._generate_config(s, rootdir=rootdir)

    def _generate_config(self, service, rootdir):
        print("generating supervisor config for " + service['name'])
        name = service['name']
        function = service.get('function')
        command = service.get('command')
        port = service['port']
        directory = "/opt/rorolite/project/" + service.get("directory", "")

        if function:
            command = '/opt/rorolite/project/.rorolite/env/bin/firefly -b 0.0.0.0:{port} {function}'.format(port=port, function=function)

        if command is None:
            raise Exception("command is not specified for service {!r}".format(name))

        path = pathlib.Path(rootdir).joinpath(".rorolite", "supervisor", name + ".conf")
        if not path.parent.exists():
            path.parent.mkdir(parents=True)

        text = SUPERVISOR_CONFIG.format(name=name, directory=directory, command=command)
        with path.open("w") as f:
            f.write(text)
