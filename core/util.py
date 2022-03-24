#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author github.com/LimerBoy

__all__ = ['login_required', 'IncidentStates']

# Import modules
from enum import Enum
from functools import wraps
from flask import (
    session,
    url_for,
    redirect,
    Response
)
# Import packages
from core.account import Account


class IncidentStates(Enum):
    WAITING_DESCRIPTION = 0
    WAITING_IMAGE = 1
    COMPLETED = 2


def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs) -> Response:
        try:
            account = Account(**session['account'])
        except KeyError:
            pass
        else:
            if account.login():
                return function(account, **kwargs)
        return redirect(url_for("login"), code=302)

    return decorated_function

