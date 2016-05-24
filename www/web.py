#! /usr/bin/env python3
# -*- encoding:utf-8 -*-

class RequestHandler(object):
    """docstring for RequestHandler"""
    def __init__(self, app, func):
        super(RequestHandler, self).__init__()
        self._app = app
        self._func = func

    def __call__(self, request):
        keyword = request
        result = yield from self._func(**keyword)
