import os
from pathlib import Path

import click
from nacl import secret
from sqlalchemy import (create_engine, MetaData, Table, Column, String, UniqueConstraint, select, and_)
from sqlalchemy.exc import IntegrityError


class Runnable(object):
    def __init__(self):
        self.path = path=Path(os.path.join(os.getenv("HOME"), '.passpy'))
        self.engine = self.__create_engine(Path(path))
        self.metadata = MetaData(self.engine)
        self.table = self.__create_table(self.metadata)

    @staticmethod
    def __create_engine(path):
        path.mkdir(exist_ok=True)
        return create_engine(f'sqlite:///{path}/passpy.config', echo=False)

    @staticmethod
    def __create_table(metadata):
        master_table = Table('passpy', metadata,
                             Column('program', String),
                             Column('username', String),
                             Column('hash', String), UniqueConstraint('program', 'username'))
        metadata.create_all()
        return master_table

    def create_passpy(self, master_password):
        master_table = Table('passpy', self.metadata,
                             Column('program', String),
                             Column('username', String),
                             Column('hash', String), UniqueConstraint('program', 'username'))
        self.metadata.create_all()
        try:
            ins = master_table.insert({'program': 'master',
                                       'username': 'passpy',
                                       'hash': self._encrypt_text(master_password, master_password)})
            self.engine.execute(ins)
        except IntegrityError:
            raise click.ClickException('Master Password already present, '
                                       'To replace, run the update command with --master-password flag')

    def add_creds(self, program, username, password):
        try:
            ins = self.table.insert({'program': program,
                                     'username': username,
                                     'hash': self._encrypt_text(password, password)})
            self.engine.execute(ins)
        except IntegrityError:
            raise click.ClickException(f'Username {username} for this Program {program} already exists, '
                                       'To update or replace, run the update command')

    def __check_creds(self, program, username):
        query = select([self.table.c.username],
                       and_(self.table.c.username == username, self.table.c.program == program))
        res = self.engine.execute(query)
        return res.fetchall()

    def update_creds(self, program, username, password):
        exists = self.__check_creds(program, username)
        if exists:
            ins = self.table.update() \
                .where(self.table.username == username, self.table.program == program) \
                .values({'hash': self._encrypt_text(password, password)})
            self.engine.execute(ins)
        else:
            raise click.ClickException(f'Username {username} for this Program {program} does not exist, '
                                       'Did you mean to add a new credential?')

    def __create_secret(self, master_password):
        key = master_password.ljust(32, 'x').encode()
        box = secret.SecretBox(key)
        return box

    def _encrypt_text(self, x, key):
        box = self.__create_secret(key)
        return box.encrypt(x.encode())

    def _decrypt_text(self, s, key):
        pass
