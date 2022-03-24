#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author github.com/LimerBoy

__all__ = ['Administrator', 'Client', 'Incident']

# Import modules
from peewee import *
from datetime import datetime


# Create database handler
SqliteHandler = SqliteDatabase('bot.sqlite')


# Base Model
class BaseModel(Model):
    id = IntegerField(null=False, unique=False, primary_key=True)

    class Meta:
        database = SqliteHandler
        order_by = ('id',)


# Administrator Model
class Administrator(BaseModel):
    username = CharField(max_length=16, null=False, unique=True)
    password = CharField(max_length=120, null=False, unique=False)

    class Meta:
        db_table = 'administrators'


# Client Model
class Client(BaseModel):
    chat_id = IntegerField(null=False, unique=True)
    full_name = CharField(null=False, unique=False)
    incident_state = IntegerField(null=False, unique=False, default=2)
    latest_incident_id = IntegerField(null=True, unique=False)
    register_date = DateTimeField(default=datetime.now, null=False, unique=False)

    class Meta:
        db_table = 'clients'


# Incident Model
class Incident(BaseModel):
    created_by_id = IntegerField(null=True, unique=False)
    image_path = CharField(default='', max_length=32, null=True, unique=False)
    description = CharField(default='', max_length=255, null=True, unique=False)
    creation_date = DateTimeField(default=datetime.now, null=False, unique=False)

    class Meta:
        db_table = 'incidents'


# Connect to database
SqliteHandler.connect()
# Create tables
SqliteHandler.create_tables([Administrator, Client, Incident])
