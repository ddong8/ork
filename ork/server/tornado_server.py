#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 21:55
# @File    : tornado_server.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import platform

from tornado import netutil
from tornado import process
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from ork.core.config import CONF
from ork.server.base_application import application


def main():
    """
    入口函数,根据操作系统类型使用多进程,
    Windows使用单进程,linux使用配置的进程数
    使用tornado的高级多进程启动方式
    :return:
    """
    # advanced multi-process
    port = CONF.server.port
    address = CONF.server.address
    num_processes = CONF.num_processes
    sockets = netutil.bind_sockets(port=port, address=address)
    if platform.system() == "Linux":
        process.fork_processes(num_processes=num_processes)
    server = HTTPServer(application, xheaders=True)
    server.add_sockets(sockets)
    print("server serving on % s:% s" % (address, port))
    IOLoop.current().start()


if __name__ == '__main__':
    main()