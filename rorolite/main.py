from __future__ import print_function
import click
from fabric.api import env as fabric_env
from . import __version__
from . import fabfile
from . import config

@click.group()
@click.version_option(version=__version__)
def cli(verbose=False):
    """rorolite is a tool to deploy ML applications to your server.
    """
    conf = config.load_config(".")
    fabric_env.hosts = [conf.host]
    fabric_env.user = conf.user

@cli.command(context_settings={"allow_interspersed_args": False})
@click.argument("command", nargs=-1)
@click.option("-w", "--workdir")
def run(command, workdir=None):
    fabfile.run_task("run_command", command=command, workdir=workdir)

@cli.command(name="run:notebook", context_settings={
    "allow_interspersed_args": False,
    "allow_extra_args": True,
    "ignore_unknown_options": True,})
@click.argument("args", nargs=-1)
@click.option("-w", "--workdir")
def run_notebook(workdir=None, args=[], **kwargs):
    fabfile.run_task("run_notebook", workdir=workdir, args=args, kwargs=kwargs)

@cli.command()
def provision():
    fabfile.run_task("provision")

@cli.command()
def deploy():
    fabfile.run_task("deploy")

@cli.command()
@click.argument("name")
@click.option("-n", default=10, type=int)
@click.option("-f", "--follow", is_flag=True, default=False)
def logs(name, n=10, follow=False):
    fabfile.run_task("logs", service=name, n=n, follow=follow)

@cli.command()
def ps():
    fabfile.run_task("supervisorctl", "status")

@cli.command()
@click.argument("name")
def stop(name):
    fabfile.run_task("supervisorctl", "stop", name)

@cli.command()
@click.argument("name")
def start(name):
    fabfile.run_task("supervisorctl", "start", name)

@cli.command()
@click.argument("name")
def restart(name):
    fabfile.run_task("supervisorctl", "restart", name)

@cli.command()
@click.argument("name")
def hello(name="world"):
    """Prints a hello world message on the remote server.
    """
    fabfile.run_task("hello", name=name)

@cli.command()
@click.argument("src")
@click.argument("dest")
def put(src, dest):
    """Copies a local file to remote server.
    """
    fabfile.run_task("putfile", src=src, dest=dest)

@cli.command()
@click.argument("src")
@click.argument("dest")
def get(src, dest):
    """Copies a file from remote server to local machine.
    """
    fabfile.run_task("getfile", src=src, dest=dest)

@cli.command()
def help():
    """Show this help message."""
    cli.main(args=[])

def main():
    cli()
