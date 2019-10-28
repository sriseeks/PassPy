"""
foo==bar
"""

import logging
import os
from pathlib import Path

import click

from .runnable import Runnable as driver

logger = logging.getLogger(__name__)
_DEBUG_FLAG = True


@click.group()
@click.pass_context
def passpy():
    pass


def create_master(password):
    click.echo(f'master password is {password}')


@click.command()
def update_master():
    pass


def insert():
    pass


def update():
    pass


def delete():
    pass


@passpy.command()
@click.option('-p', '--path', default=Path(os.path.join(os.getenv("HOME"), '.passpy')),
              help='Path for a new PassPy Database')
def new(path):
    """Create a new PassPy configuration"""
    if path != Path(os.path.join(os.getenv("HOME"), '.passpy')):
        raise NotImplementedError("Custom PassPy config path is not yet implemented")
    master_password = click.prompt('Enter master-password', hide_input=True, confirmation_prompt=True)
    driver().create_passpy(master_password)
    click.echo('New PassPy Database created. Please keep your master password in a secure location')


@passpy.command()
def add():
    click.echo("Adding new PassPy entry...")
    program = click.prompt('Program name')
    username = click.prompt('Enter username')
    password = click.prompt('Enter password', hide_input=True, confirmation_prompt=True)
    driver().add_creds(program, username, password)
    click.echo('Your credentials are secured in PassPy')


@passpy.command()
def update():
    click.echo("Updating PassPy entry...")
    program = click.prompt('Program name')
    username = click.prompt('Enter username')
    password = click.prompt('Enter password', hide_input=True, confirmation_prompt=True)
    driver().update_creds(program, username, password)
    click.echo('Your credentials are secured in PassPy')


@passpy.command()
def delete():
    pass


cli = click.CommandCollection(sources=[passpy])

if __name__ == '__main__':
    cli(obj={})
