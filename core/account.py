#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author github.com/LimerBoy

__all__ = ['Account']

# Import modules
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
# Import packages
from core.db import Administrator


# Account object
class Account(object):

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def login(self) -> bool:
        for client in Administrator.select().where(Administrator.username == self.username):
            return check_password_hash(client.password, self.password)

    def register(self) -> bool:
        Administrator.create(
            username=self.username,
            password=generate_password_hash(self.password)
        )
        return True

    def set_password(self, password: str):
        Administrator.update(
            password=generate_password_hash(password)
        ).where(
            Administrator.username == self.username
        ).execute()

