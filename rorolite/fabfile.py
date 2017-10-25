import pathlib
from fabric.api import task, run, env, cd, sudo, put
from fabric.tasks import execute, Task
from .utils import hijack_output_loop
from .deploy import Deployment
from . import config

# Fabric prints all the messages with a '[hostname] out:' prefix.
# Hijacking it to remove the prefix
hijack_output_loop()

@task
def hello(name="world"):
    with cd("."):
        run("echo hello " + name)

@task
def run_command(command, workdir=None):
    workdir = workdir or "/opt/rorolite/project"
    command_str = " ".join(command)
    with cd(workdir):
        run(command_str)

@task
def run_notebook(workdir=None, args=None, kwargs=None):
    args = args or []
    kwargs = kwargs or {}
    print("host", env.host)
    command = "jupyter notebook --ip {host} --allow-root".format(host=env.host).split() + list(args)
    return run_command(command, workdir=workdir)

@task
def restart(service):
    sudo("supervisorctl restart " + service)

@task
def logs(service, n=10, follow=False):
    follow_flag = "-f" if follow else ""
    cmd = "tail -n {} {} /var/log/supervisor/{}.log".format(n, follow_flag, service)
    sudo(cmd)

@task
def deploy():
    d = Deployment()
    d.deploy()

@task
def provision():
    sudo("apt-get update")
    sudo("apt-get install -y " + " ".join(config.system_packages))
    install_anaconda(config.anaconda_version)

@task
def supervisorctl(*args):
    sudo("supervisorctl " + " ".join(args))

def install_anaconda(version):
    print("installing anaconda {}...".format(version))
    url = config.anaconda_download_url_format.format(version=version)
    print("downloading", url)
    path = "/tmp/" + url.split("/")[-1]
    run("wget -O {path}.tmp {url} && mv {path}.tmp {path}".format(path=path, url=url))
    run("rm -rf /opt/anaconda3")
    run("bash {path} -b -p /opt/anaconda3".format(path=path))

    path = pathlib.Path(__file__).parent / "files" / "etc" / "profile.d" / "rorolite.sh"
    put(str(path), "/etc/profile.d/rorolite.sh")

def run_task(taskname, *args, **kwargs):
    task = globals().get(taskname)
    if isinstance(task, Task):
        execute(task, *args, **kwargs)
    else:
        raise Exception("Invalid task: " + repr(taskname))
