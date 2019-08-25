"""
My First Python Project
"""

import os
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer
import nacl
import pyperclip
from pathlib import Path
from nacl import secret
import click

def create_engine(path=None):
    path = Path(f'{os.getenv("HOME")}/.passpy')
    path.mkdir(exist_ok=True)
    return create_engine(f'sqlite:///{path}/passpy.config', echo=False)


def create_passpy(path):
    engine = create_engine(path)
    metadata = MetaData(engine)
    master_table = Table('passpy', metadata,
                         Column('id', Integer, primary_key=True, autoincrement=True),
                         Column('program', String),
                         Column('username', String),
                         Column('hash', String))
    metadata.create_all()


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


def _encrypt_text():
    pass

@click.command()
def passpy(master_password):
    if master_password:
        create_master(master_password)

# @click.option('-n', '--new', default=os.getenv("HOME"), help='Create a new PassPy database')
# @click.option('-a', '--add', help='Add new credentials to PassPy', prompt=True, multiple=True)
# @click.option('--master-password', prompt=True, hide_input=True, confirmation_prompt=True)


@click.command()
def cli():
    pass