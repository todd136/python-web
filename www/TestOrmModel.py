#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import orm, model

def test():
    yield from orm.create_pool(user='root', password='123456', database='blog')
    u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
    yield from u.save()

if __name__ == '__main__':
    test()
