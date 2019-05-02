#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:24
# @File    : decorators.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import functools
import sys
import threading


def singleton(cls):
    """单例模式装饰器"""
    instances = {}
    lock = threading.Lock()

    def _singleton(*args, **kwargs):
        with lock:
            fullkey = str((cls.__name__, tuple(args), tuple(kwargs.items())))
            if fullkey not in instances:
                instances[fullkey] = cls(*args, **kwargs)
        return instances[fullkey]

    return _singleton


def protect(callback):
    """
    提供权限认证回调
    callback = func(creds, action)
    """

    def _protect(func):
        @functools.wraps(func)
        def __protect(resource, req, resp, *args, **kwargs):
            # eg. {'user': 'roy', 'roles':['admin'], 'token': '', 'tenant': 'tenant-uuid'}
            creds = req.x_auth
            obj = resource.__module__ + "." + resource.__class__.__name__
            obj = obj.lower()
            action = func.__name__.lower()
            callback(creds, action, obj)
            return func(resource, req, resp, *args, **kwargs)

        return __protect

    return _protect


def require(mod_name, attr_name):
    """
    基于描述符的延迟加载
    :param mod_name: a.b.c:class
    :param attr_name: attrubute name
    """

    class _lazy_attribute(object):
        def __init__(self, mod_name):
            mods = mod_name.split(':')
            self.mod_name = mods[0]
            self.attr_name = mods[1] if len(mods) > 1 else None

        def __get__(self, instance, owner):
            if self.mod_name not in sys.modules:
                __import__(self.mod_name)
            mod = sys.modules[self.mod_name]
            if self.attr_name:
                return getattr(mod, self.attr_name)
            return mod

    def _require_api(cls):
        def __require_api(*args, **kwargs):
            setattr(cls, attr_name, _lazy_attribute(mod_name))
            instance = cls(*args, **kwargs)
            return instance

        return __require_api

    return _require_api