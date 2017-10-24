from fabric.api import task, run, env, cd, sudo
from fabric.tasks import execute, Task
import logging

logger = logging.getLogger("rorolite")

env.hosts = ['localhost']

@task
def hello(name="world"):
    with cd("."):
        run("echo hello " + name)

@task
def run_command(command, workdir="."):
    command_str = " ".join(command)
    with cd(workdir):
        run(command_str)

def run_task(taskname, **kwargs):
    task = globals().get(taskname)
    logger.info("executing task %s", taskname)
    if isinstance(task, Task):
        execute(task, **kwargs)
    else:
        raise Exception("Invalid task: " + repr(taskname))
