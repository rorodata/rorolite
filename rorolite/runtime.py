"""
    rorolite.runtime
    ~~~~~~~~~~~~~~~~

    This module implements support for multiple rorolite runtimes.
"""
from fabric.api import sudo, put, cd
from pkg_resources import resource_listdir, resource_exists, resource_filename, resource_stream
import yaml
import pathlib

DEFAULT_RUNTIME = "python3"

class Runtime(object):
    """Runtime represents a software setup.

    Some examples of runtimes are python3, python3-keras, raspberrypi-python3-keras
    etc.

    The runtime object contains all the metadata required to install
    all the required software on a computer.

    It provides an `install` method, which is supposed to be called
    from a fabric task. It'll perform some actions on the remote
    machine to complete the setup.
    """
    def __init__(self, name, version, data):
        self.root = resource_filename(__name__, "runtimes/" + name)
        self.name = name
        self.version = version
        self.data = data
        self.init()

    def __repr__(self):
        return "<Runtime:{}>".format(self.name)

    def init(self):
        self.apt_packages = self.data.get("apt_packages", [])
        self.pip_packages = self.data.get("pip_packages", [])
        self.python_binary = self.data.get("python_binary", "python")
        self.before_scripts = self.data.get("before_scripts", [])
        self.after_scripts = self.data.get("after_scripts", [])

    def install(self):
        """Installs the runtime on a remote machine.

        This method must be called only from a fabric task.
        """
        target = "/tmp/rorolite-runtime/" + self.name
        sudo("mkdir -p " + target)

        put(self.root, "/tmp/rorolite-runtime", use_sudo=True)
        if self.before_scripts:
            with cd(target):
                for s in self.before_scripts:
                    print("executing", s)
                    sudo(s)

        if self.apt_packages:
            sudo("apt-get -q update")
            sudo("apt-get -q -y install " + " ".join(self.apt_packages))

        if self.pip_packages:
            sudo("{} -m pip -q install {}".format(
                self.python_binary, " ".join(self.pip_packages)))

        if self.after_scripts:
            with cd(target):
                for s in self.after_scripts:
                    print("executing", s)
                    sudo(s)

        self.setup_system_path()

    def setup_system_path(self):
        path = pathlib.Path(__file__).parent / "files" / "etc" / "profile.d" / "rorolite.sh"
        put(str(path), "/etc/profile.d/Z99-rorolite.sh", use_sudo=True)

    @classmethod
    def all(cls):
        def is_runtime(name):
            return resource_exists("runtimes/{}/runtime.yml".format(name))

        names = resource_listdir(__name__, "runtimes")
        names = [is_runtime(name) for name in names]
        return [cls.load(name) for name in names]

    @classmethod
    def load(cls, name):
        """Loads the runtime of the specified name.
        """
        f = resource_stream(__name__, "runtimes/{}/runtime.yml".format(name))
        data = yaml.safe_load(f)
        return Runtime(data['name'], data['version'], data)
