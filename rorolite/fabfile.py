from __future__ import print_function
from fabric.api import task, run, env, cd, sudo, put, get
from fabric.tasks import execute, Task
from .utils import hijack_output_loop
from .deploy import Deployment
from .project import Project

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
    project = Project()
    project.runtime.install()
    setup_volumes()

@task
def putfile(src, dest):
    put(src, dest)

@task
def getfile(src, dest):
    get(src, dest)

@task
def supervisorctl(*args):
    sudo("supervisorctl " + " ".join(args))

def setup_volumes():
    sudo("mkdir -p /volumes/data")
    sudo("chown {} /volumes".format(env.user))
    sudo("chown {} /volumes/data".format(env.user))

def run_task(taskname, *args, **kwargs):
    task = globals().get(taskname)
    if isinstance(task, Task):
        execute(task, *args, **kwargs)
    else:
        raise Exception("Invalid task: " + repr(taskname))
