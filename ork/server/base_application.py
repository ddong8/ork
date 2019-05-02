#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 21:55
# @File    : base_application.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import os
import sys

import tornado.options
import tornado.web

from ork.core import config
from ork.db import pool
from ork.middleware import get_middleware

CONF = config.CONF


def initialize_database():
    """
    初始化数据库连接池
    :return: 数据库连接池 pool
    """
    pool.POOL.refresh(param={'connection': CONF.db.connection,
                             'pool_size': CONF.db.pool_size,
                             'pool_recycle': CONF.db.pool_recycle,
                             'pool_timeout': CONF.db.pool_timeout,
                             'max_overflow': CONF.db.max_overflow}, connecter='psycopg2')


def initialize_logger():
    """
    automatically enabled by tornado.options.parse_command_line
    or tornado.options.parse_config_file
    """
    tornado.options.options.log_file_prefix = str(CONF.log.path)
    tornado.options.options.log_to_stderr = CONF.log.stderr
    tornado.options.parse_command_line()


def initialize_config(path):
    """
    初始化配置文件
    :param path: 配置文件的路径
    :return: 配置变量 CONF
    """
    config.setup(path)


def initialize_application(api):
    """
    初始化应用,动态添加路由
    :param api: 应用实例
    :return: 添加路由的应用实例
    """
    for name in CONF.application.names:
        if name:
            __import__(name)
            app = sys.modules[name]
            app.route.add_routes(api)
    tornado.web.Application.__init__(api, debug=api.debug, handlers=api.handlers, **api.settings)


def initialize_server():
    """
    初始化server
    1.初始化配置文件
    2.初始化日志
    3.初始化数据库
    4.初始化应用
    :return:应用实例
    """
    initialize_config('/etc/ork/ork.json')
    initialize_logger()
    initialize_database()
    api = Application()
    initialize_application(api)
    return api


class Application(tornado.web.Application):
    """
    继承tornado.web.Application类,
    初始化应用设置,初始化中间件,动态添加路由
    """

    def __init__(self):
        self.settings = dict()
        self.middleware = get_middleware()
        self.handlers = []
        self.debug = CONF.debug

    def add_route(self, uri_template, resource):
        self.handlers.append((uri_template, resource))


application = initialize_server()