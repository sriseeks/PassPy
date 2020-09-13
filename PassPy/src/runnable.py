import os
from pathlib import Path

import click
import pandas
from nacl import secret
from sqlalchemy import (create_engine, MetaData, Table, Column, String, UniqueConstraint, select, and_)
from sqlalchemy.exc import IntegrityError


class Runnable(object):
    def __init__(self):
        self.path = Path(os.path.join(os.getenv("HOME"), '.passpy'))
        self.engine = self.__create_engine(Path(self.path))
        self.metadata = MetaData(self.engine, reflect=True)
        self.table = self.__create_table(self.metadata)
        self.master_table = self.get_master_table()

    @staticmethod
    def __create_engine(path):
        path.mkdir(exist_ok=True)
        return create_engine(f'sqlite:///{path}/passpy.config', echo=False)

    def __create_table(self, metadata):
        table = Table('passpy', metadata,
                      Column('program', String),
                      Column('username', String),
                      Column('hash', String), UniqueConstraint('program', 'username'),
                      extend_existing=True)
        if 'passpy' not in metadata.tables.keys():
            metadata.create_all(bind=self.engine)
        return table

    def create_passpy(self, master_password):
        try:
            ins = self.master_table.insert({'program' : 'master',
                                            'username': 'passpy',
                                            'hash'    : self._encrypt_text(master_password, master_password)})
            self.engine.execute(ins)
        except IntegrityError:
            raise click.ClickException('Master Password already present, '
                                       'To replace, run the update command with -m/--master flag')

    def get_master_table(self):
        master_table = Table('master', self.metadata,
                             Column('program', String),
                             Column('username', String),
                             Column('hash', String), UniqueConstraint('program', 'username'),
                             extend_existing=True)
        self.metadata.create_all(bind=self.engine)
        return master_table

    def add_creds(self, program, username, password, master):
        try:
            ins = self.table.insert({'program' : program,
                                     'username': username,
                                     'hash'    : self._encrypt_text(password, master)})
            self.engine.execute(ins)
        except IntegrityError:
            raise click.ClickException(f'Username {username} for this Program {program} already exists, '
                                       'To update or replace, run the update command')

    def __check_creds(self, program, username):
        query = select([self.table.c.username],
                       and_(self.table.c.username == username, self.table.c.program == program))
        res = self.engine.execute(query)
        return res.fetchall()

    def update_creds(self, program, username, password, master, is_master=False):
        if is_master:
            ins = self.master_table.update() \
                .where(and_(self.master_table.c.username == 'passpy', self.master_table.c.program == 'master')) \
                .values({'hash': self._encrypt_text(password, master)})
            self.engine.execute(ins)
        else:
            exists = self.__check_creds(program, username)
            if exists:
                ins = self.table.update() \
                    .where(and_(self.table.c.username == username, self.table.c.program == program)) \
                    .values({'hash': self._encrypt_text(password, master)})
                self.engine.execute(ins)
            else:
                raise click.ClickException(f'Username {username} for this Program {program} does not exist, '
                                           'Did you mean to add a new credential?')

    def delete_creds(self, program, username):
        query = self.table.delete().where(and_(self.table.c.program == program, self.table.c.username == username))
        self.engine.execute(query)

    def validate_master(self, master_password):
        # TODO: check if record exists; raise error appropriately
        query = select([self.master_table.c.hash],
                       and_(self.master_table.c.username == 'passpy', self.master_table.c.program == 'master'))
        res = self.engine.execute(query)
        try:
            if res and self._decrypt_text(res.fetchall()[0][0], master_password) == master_password.encode():
                return True
            else:
                return False
        except:
            return False

    def get_creds(self, program, master):
        query = select([self.table.c.username, self.table.c.hash], self.table.c.program == program)
        res = self.engine.execute(query)
        try:
            if res:
                creds = res.fetchall()
                username = creds[0][0]
                password = self._decrypt_text(creds[0][1], master).decode()
                return username, password
            else:
                return False
        except:
            return False

    def list_objects(self):
        query = select([self.table.c.program, self.table.c.username])
        res = self.engine.execute(query)
        try:
            objects = pandas.DataFrame(res.fetchall(), columns=['program', 'username'])
            return objects
        except Exception as e:
            click.ClickException(e)
            return False

    @staticmethod
    def __create_secret(master_password):
        key = master_password.ljust(32, 'x').encode()
        box = secret.SecretBox(key)
        return box

    def _encrypt_text(self, s, key):
        box = self.__create_secret(key)
        return box.encrypt(s.encode())

    def _decrypt_text(self, s, key):
        box = self.__create_secret(key)
        return box.decrypt(s)
