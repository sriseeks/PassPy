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


@passpy.command()
@click.option('-p', '--path', default=Path(os.path.join(os.getenv("HOME"), '.passpy')),
              help='Path for a new PassPy Database')
def new(path):
    """Create a new PassPy configuration"""
    if path != Path(os.path.join(os.getenv("HOME"), '.passpy')):
        raise click.ClickException("Custom PassPy config path is not yet implemented. Lookout for future versions..")
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


def _update_master():
    click.echo("Updating PassPy Master Password...")
    master = click.prompt("For security purpose please enter the master password", hide_input=True,
                          confirmation_prompt=True)
    result = driver().validate_master(master)
    if result:
        master = click.prompt('Enter new Master Password', hide_input=True, confirmation_prompt=True)
        driver().update_creds(program='master', username='passpy', password=master)
        click.echo('Successfully updated Master Password')
    else:
        click.echo("Wrong credentials, Please try again")


def update_creds():
    click.echo("Updating PassPy entry...")
    master = click.prompt("For security purpose please enter the master password", hide_input=True,
                          confirmation_prompt=True)
    result = driver().validate_master(master)
    if result:
        program = click.prompt('Program name')
        username = click.prompt('Enter username')
        password = click.prompt('Enter password', hide_input=True, confirmation_prompt=True)
        driver().update_creds(program, username, password)
        click.echo('Your credentials are securely updated in PassPy')
    else:
        click.echo("Wrong credentials, Please try again")


@passpy.command()
@click.option('-m', '--master', help='Flag to update master password', is_flag=True, required=False)
def update(master=None):
    if master:
        _update_master()
    else:
        update_creds()


@passpy.command()
def remove():
    click.echo("Deleting PassPy entry...")
    click.echo("For security purpose, please enter master password...")
    master = click.prompt("For security purpose please enter the master password", hide_input=True,
                          confirmation_prompt=True)
    result = driver().validate_master(master)
    if result:
        program = click.prompt('Program name')
        username = click.prompt('Enter username')
        driver().delete_creds(program, username)
        click.echo('Your credentials are securely updated in PassPy')
    else:
        click.echo("Wrong credentials, Please try again")


cli = click.CommandCollection(sources=[passpy])

if __name__ == '__main__':
    cli(obj={})
