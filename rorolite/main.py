from __future__ import print_function
import click
from fabric.api import env as fabric_env
from . import __version__
from . import fabfile

@click.group()
@click.version_option(version=__version__)
def cli(verbose=False):
    """rorolite is a tool to deploy ML applications to your server.
    """

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
def hello(name="world"):
    """Prints a hello world message on the remote server.
    """
    fabfile.run_task("hello", name=name)

@cli.command()
def help():
    """Show this help message."""
    cli.main(args=[])

def main():
    cli()
