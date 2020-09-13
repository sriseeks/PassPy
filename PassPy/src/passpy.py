import logging
import os
import time
from pathlib import Path

import click
import pyperclip
from tqdm import tqdm

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
    """Add new credential to PassPy"""
    # TODO: add check to verify if master password exists
    master = click.prompt("For security purpose please enter the master password", hide_input=True,
                          confirmation_prompt=False)
    result = driver().validate_master(master)
    if result:
        click.echo("Adding new PassPy entry...")
        program = click.prompt('Program name')
        username = click.prompt('Enter username')
        password = click.prompt('Enter password', hide_input=True, confirmation_prompt=True)
        driver().add_creds(program, username, password, master)
        click.echo('Your credentials are secured in PassPy')
    else:
        click.echo("Wrong credentials, Please try again")


def _update_master():
    click.echo("Updating PassPy Master Password...")
    master = click.prompt("For security purpose please enter the master password", hide_input=True,
                          confirmation_prompt=False)
    result = driver().validate_master(master)
    if result:
        master = click.prompt('Enter new Master Password', hide_input=True, confirmation_prompt=True)
        driver().update_creds(program='master', username='passpy', password=master, master=master, is_master=True)
        click.echo('Successfully updated Master Password')
    else:
        click.echo("Wrong credentials, Please try again")


def update_creds():
    click.echo("Updating PassPy entry...")
    master = click.prompt("For security purpose please enter the master password", hide_input=True,
                          confirmation_prompt=False)
    result = driver().validate_master(master)
    if result:
        program = click.prompt('Program name')
        username = click.prompt('Enter username')
        password = click.prompt('Enter password', hide_input=True, confirmation_prompt=True)
        driver().update_creds(program, username, password, master)
        click.echo('Your credentials are securely updated in PassPy')
    else:
        click.echo("Wrong credentials, Please try again")


@passpy.command()
@click.option('-m', '--master', help='Flag to update master password', is_flag=True, required=False)
def update(master=None):
    """Update existing credentials"""
    if master:
        _update_master()
    else:
        update_creds()


@passpy.command()
def remove():
    """Delete PassPy Credentials"""
    click.echo("Deleting PassPy entry...")
    master = click.prompt("For security purpose please enter the master password", hide_input=True,
                          confirmation_prompt=False)
    result = driver().validate_master(master)
    if result:
        program = click.prompt('Program name')
        username = click.prompt('Enter username')
        driver().delete_creds(program, username)
        click.echo('Your credentials are removed from PassPy')
    else:
        click.echo("Wrong credentials, Please try again")


@passpy.command()
@click.option('-p', '--password-only', help='Password Only?', is_flag=True, required=False)
def get(password_only=False):
    """Get an existing credential from PassPy"""
    master = click.prompt("For security purpose please enter the master password", hide_input=True,
                          confirmation_prompt=False)
    result = driver().validate_master(master)
    if result:
        program = click.prompt('Program name')
        res = driver().get_creds(program, master)
        if res:
            username, password = res
            if not password_only:
                pyperclip.copy(username)
                for _ in tqdm(range(1, 15), desc='Username copied to clipboard. Expires in ..', ncols=100,
                              bar_format='{l_bar}{bar}'): time.sleep(1)
                pyperclip.copy('')
            pyperclip.copy(password)
            for _ in tqdm(range(1, 15), desc='Password copied to clipboard. Expires in ..', ncols=100,
                          bar_format='{l_bar}{bar}'):
                time.sleep(1)
            pyperclip.copy('')
        else:
            click.echo('The program is unavailable. Please try again. To add a new credential, run passpy add')
    else:
        click.echo("Wrong credentials, Please try again")


@passpy.command()
def list():
    """Get an existing credential from PassPy"""
    master = click.prompt("For security purpose please enter the master password", hide_input=True,
                          confirmation_prompt=False)
    result = driver().validate_master(master)
    if result:
        res = driver().list_objects()
        if len(res) > 0:
            click.echo(f"Below's all the credential stored\n"
                       f"{res}")
    else:
        click.echo("Wrong credentials, Please try again")


cli = click.CommandCollection(sources=[passpy])

if __name__ == '__main__':
    cli(obj={})
