#! /usr/bin/env python3
# -*- encoding:utf-8 -*-

from orm import Model, StringField, FloatField, TextField, BooleanField
import time
import logging; logging.basicConfig(level=logging.INFO)

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    """docstring for User"""
    __table__ = 't_user'

    fid = StringField(primary_key=True, default=next_id, ddl = 'varchar(50)')
    email = StringField(ddl = 'varchar(50)')
    name = StringField(ddl = 'varchar(50)')
    passwd = StringField(ddl = 'varchar(50)')
    admin = BooleanField()
    image = StringField(ddl = 'varchar(500)')
    create_time = FloatField(default = time.time)

class Blog(Model):
    """docstring for Blog"""
    __table__ = 't_blog'

    fid = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    userId = StringField(ddl = 'varchar(50)')
    userName = StringField(ddl = 'varchar(50)')
    userImage = StringField(ddl = 'varchar(500')
    name = StringField(ddl = 'varchar(50)')
    sumary = StringField(ddl = 'varchar(500)')
    content = TextField()
    create_time = FloatField(default = time.time)

class Comment(Model):
    """docstring for Comment"""
    __table__ = 't_comment'

    fid = StringField(primary_key = True, default = next_id, ddl = 'varchar(50)')
    blogId = StringField(ddl = 'varchar(50)')
    userId = StringField(ddl = 'varchar(50)')
    userName = StringField(ddl = 'varchar(50)')
    userImage = StringField(ddl = 'varchar(500')
    content = TextField()
    create_time = FloatField(default = time.time)

