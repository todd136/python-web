#! /usr/bin/env python3
# -*- encoding:utf-8 -*-

import asyncio
import logging; logging.basicConfig(level=logging.INFO)

@asyncio.coroutine
def create_pool(loop, **keyword):
    global __pool
    __pool = yield from aiomysql.create_pool(
        host = keyword.get('host', 'localhost'),
        port = keyword.get('port', 3306),
        user = keyword['user'],
        password = keyword['password'],
        db = keyword['db'],
        charset = keyword.get('charset', 'uft-8'),
        autocommit = keyword.get('autocommit', True),
        maxsize = keyword.get('maxsize', 10),
        minsize = keyword.get('minsize', 1),
        loop = loop
        )

@asyncio.coroutine
def select(sql, args, size = None):
    log(sql, args)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows returned: %s' % lens(rs))
        return rs

@asyncio.coroutine
def execute(sql, args):
    log(sql)
    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor(aiomysql.DictCursor)
            yield from cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            yield from cur.close()
        except Exception as e:
            raise e
        finally:
            return affected

def create_args_string(num):
    L = []
    for x in range(num):
        L.append('?')
    return ', '.join(L)

class ModelMetaclass(type):
    """docstring for ModelMetaclass"""
    def __new__(cls, name, bases, attris):
        if name == 'Model':
            return type.__new__(cls, name, bases, attris)
        tableName = attris.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attris.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError('Duplicated primary key for field:%s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('Primary key not found')
        for k in mappings.keys():
            attris.pop(k)
        escaped_fields = list(map(lambda f: '%s' % f, fields))
        attris['__mapping__'] = mappings
        attris['__table__'] = tableName
        attris['__primary_key__'] = primaryKey
        attris['__fields__'] = fields

        attris['__select__'] = 'select %s, %s from %s' % (primaryKey, ', '.join(escaped_fields), tableName)
        attris['__insert__'] = 'insert into %s (%s, %s) values(%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields)+1))
        attris['__update__'] = 'update %s set %s where %s = ?' % (tableName, ', '.join(map(lambda f: '%s = ?' % (mappings.get(f).name or f), fields)), primaryKey)
        attris['__delete__'] = 'delete from %s where %s = ?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attris)

class Model(dict, metaclass=ModelMetaclass):
    """docstring for Model"""
    def __init__(self, **keyword):
        super(Model, self).__init__(**keyword)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mapping__[Key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        'find object by primary key'
        rs = yield from select('%s where %s = ?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        else:
            return cls(**rs[0])

    @asyncio.coroutine
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rowCount = yield from execute(self.__insert__, args)
        if rowCount != 1:
            logging.warning('failed to insert record, affected rows:%s' % rowCount)

    @asyncio.coroutine
    def findAll(self, whereClause, args):
        rs = yield from select('%s where %s' % (self.__select__, whereClause), args)
        if len(rs) == 0:
            return None
        else:
            return rs

    @asyncio.coroutine
    def fundNumber(self, whereClause, args):
        rs = yield from select('select count(*) from %s where %s' % (self.__table__, whereClause), args)
        if rs != 0:
            return rs
        else:
            logging.warning('failed to find any records match %s %s' % (whereClause, args))

    @asyncio.coroutine
    def update(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rowCount = yield from execute(self.__update__, args)
        if rowCount != 1:
            logging.warning('failed to update record, affected rows:%s' % rowCount)

    @asyncio.coroutine
    def remove(self, pk):
        rowCount = yield from execute(self.__delete__, [pk])
        if(rowCount != 1):
            logging.warning('fail to delete recode, affected rows:%s' % rowCount)

class Field(object):
    """docstring for Field"""
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):
    """docstring for StringField"""
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super(StringField, self).__init__(name, ddl, primary_key, default)

class BooleanField(Field):
    """docstring for BooleanField"""
    def __init__(self, name=None, primary_key=False, default=None, ddl='boolean'):
        super(BooleanField, self).__init__(name, ddl, primary_key, default)

class TextField(Field):
    """docstring for TextField"""
    def __init__(self, name=None, primary_key=False, default=None, ddl='text'):
        super(TextField, self).__init__(name, ddl, primary_key, default)

class FloatField(Field):
    """docstring for FloatField"""
    def __init__(self, name=None, primary_key=False, default=None, ddl='float'):
        super(FloatField, self).__init__(name, ddl, primary_key, default)

